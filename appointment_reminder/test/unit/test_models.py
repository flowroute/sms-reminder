import pytest
from datetime import datetime, timedelta

from appointment_reminder.app import app
from appointment_reminder.models import Reminder
from appointment_reminder.database import db_session
from appointment_reminder.settings import TEST_DB


def teardown_module(module):
    if TEST_DB in app.config['SQLALCHEMY_DATABASE_URI']:
        Reminder.query.delete()
        db_session.commit()
    else:
        raise AttributeError(("The production database is turned on. "
                              "Flip settings.DEBUG to True"))


def setup_module(module):
    if TEST_DB in app.config['SQLALCHEMY_DATABASE_URI']:
        Reminder.query.delete()
        db_session.commit()
    else:
        raise AttributeError(("The production database is turned on. "
                              "Flip settings.DEBUG to True"))


def test_reminder_init():
    contact = '12223334444'
    appt_str_time = '2016-01-01 13:00'
    appt_dt = datetime.strptime(appt_str_time, '%Y-%m-%d %H:%M')
    notify_win = 24
    location = 'Family Physicians'
    participant = 'Dr Smith'
    reminder = Reminder(contact, appt_str_time, notify_win,
                        location, participant)
    assert reminder.contact_num == contact
    assert reminder.id is not None
    assert reminder.appt_dt == appt_dt
    assert reminder.notify_dt == appt_dt - timedelta(hours=notify_win)
    assert reminder.location == location
    assert reminder.participant == participant


def test_clean_expired():
    contact = '12223334444'
    appt_str_time_0 = '2016-01-01 13:00'
    notify_win = 24
    location = 'Family Physicians'
    participant_0 = 'Dr Smith'
    reminder_0 = Reminder(contact, appt_str_time_0, notify_win,
                          location, participant_0)
    appt_str_time_1 = '2020-01-01 13:00'
    participant_1 = 'Dr John'
    reminder_1 = Reminder(contact, appt_str_time_1, notify_win,
                          location, participant_1)
    db_session.add(reminder_0)
    db_session.add(reminder_1)
    db_session.commit()
    stored_reminders = Reminder.query.all()
    assert len(stored_reminders) == 2
    Reminder.clean_expired()
    stored_reminders = Reminder.query.all()
    assert len(stored_reminders) == 1
    assert stored_reminders[0].participant == participant_1
