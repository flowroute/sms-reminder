import pytest
import json
import mock
from datetime import datetime, timedelta

from appointment_reminder.settings import TEST_DB
from appointment_reminder.database import db_session
from appointment_reminder.models import Reminder
from appointment_reminder.app import app


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
def appointment_details():
    content = {'contact_number': '12223334444',
               'appointment_time': '2020-01-01 13:00',
               'notify_window': '24',
               'location': 'Flowroute',
               'participant': 'Casey',
               }
    return content


@mock.patch('appointment_reminder.api.send_reminder')
def test_add_reminder_success(mock_send_reminder, appointment_details):
    client = app.test_client()
    client.post('/reminder', data=json.dumps(appointment_details),
                content_type='application/json')
    assert mock_send_reminder.apply_async.called == 1
    call_args = mock_send_reminder.apply_async.call_args
    reminder_time = appointment_details['appointment_time']
    dt = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
    notify_dt = dt - timedelta(hours=int(appointment_details['notify_window']))
    reminder_id = call_args[1]['args'][0]
    reminder = Reminder.query.one()
    assert reminder.id == reminder_id
    assert call_args[1]['eta'] == notify_dt
