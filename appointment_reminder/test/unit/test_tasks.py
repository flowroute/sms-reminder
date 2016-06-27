import pytest
import mock

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
            '2020-01-01 13:00',
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
    assert msg == ("[Your Org Name] This a reminder for your 2020-01-01 "
                   "13:00:00 appointment at Central Park with NY Running Club."
                   " Please reply 'Yes' to confirm, or 'No' to cancel.")
