import pytest
import mock
import arrow

from appointment_reminder.database import db_session
from appointment_reminder.tasks import send_reminder
from appointment_reminder.settings import TEST_DB
from appointment_reminder.service import reminder_app as app
from appointment_reminder.models import Reminder


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


@pytest.fixture
def new_reminder():
    args = ['12223334444',
            arrow.get('2015-03-23').replace(hours=+12),
            24,
            'Central Park',
            'NY Running Club',
            ]
    reminder = Reminder(*args)
    db_session.add(reminder)
    db_session.commit()
    return reminder


@mock.patch('appointment_reminder.tasks.sms_controller')
def test_send_reminder(mock_sms_controller, new_reminder):
    send_reminder(new_reminder.id)
    assert mock_sms_controller.create_message.called == 1
    msg = mock_sms_controller.create_message.call_args[0][0].content
    assert msg == ("[Your Org Name] You have an appointment on Monday, Mar 23 "
                   "12:00 PM at Central Park with NY Running Club. Please "
                   "reply 'Yes' to confirm, or 'No' to cancel.")
