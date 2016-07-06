import pytest
import json
import mock
import pendulum
from sqlalchemy.orm.exc import NoResultFound

from appointment_reminder.settings import TEST_DB
from appointment_reminder.database import db_session
from appointment_reminder.models import Reminder
from appointment_reminder.service import reminder_app as app


def teardown_module(module):
    if TEST_DB in app.config['SQLALCHEMY_DATABASE_URI']:
        Reminder.query.delete()
        db_session.commit()
    else:
        raise AttributeError(("The production database is turned on. "
                              "Flip settings.DEBUG to True"))


def setup_function(function):
    if TEST_DB in app.config['SQLALCHEMY_DATABASE_URI']:
        Reminder.query.delete()
        db_session.commit()
    else:
        raise AttributeError(("The production database is turned on. "
                              "Flip settings.DEBUG to True"))

REMINDER_FIELDS = ('contact_number', 'participant', 'reminder_id',
                   'appt_datetime', 'location', 'has_confirmed', 'notify_at')


@pytest.fixture
def appointment_details():
    content = {'contact_number': '12223334444',
               'appointment_time': '2020-01-01T13:00:00+0300',
               'notify_window': '24',
               'location': 'Flowroute',
               'participant': 'Casey',
               }
    return content


@pytest.fixture
def new_appointment():
    contact = '1222333555'
    appt_str_time_0 = '2030-01-01T13:00:00+0000'
    notify_win = 24
    location = 'Flowroute HQ'
    participant_0 = 'Development Teams'
    reminder = Reminder(contact, appt_str_time_0, notify_win,
                        location, participant_0)
    return reminder


@pytest.fixture
def new_appointments(new_appointment):
    contact = '12223334444'
    appt_str_time_0 = '2016-01-01T13:00:00+0700'
    notify_win = 24
    location = 'Family Physicians'
    participant_0 = 'Dr Smith'
    reminder_0 = Reminder(contact, appt_str_time_0, notify_win,
                          location, participant_0)
    appt_str_time_1 = '2020-01-01T13:00:00+0000'
    participant_1 = 'Dr Martinez'
    reminder_1 = Reminder(contact, appt_str_time_1, notify_win,
                          location, participant_1)
    db_session.add(reminder_0)
    db_session.add(reminder_1)
    db_session.add(new_appointment)
    db_session.commit()
    return [reminder_0, reminder_1, new_appointment]


@mock.patch('appointment_reminder.api.send_reminder')
def test_add_reminder_success(mock_send_reminder, appointment_details):
    client = app.test_client()
    resp = client.post('/reminder', data=json.dumps(appointment_details),
                       content_type='application/json')
    assert resp.status_code == 200
    assert mock_send_reminder.apply_async.called == 1
    call_args = mock_send_reminder.apply_async.call_args
    reminder_time = appointment_details['appointment_time']
    dt = pendulum.Pendulum.strptime(reminder_time, '%Y-%m-%dT%H:%M:%S%z')
    notify_dt = dt - timedelta(hours=int(appointment_details['notify_window']))
    reminder_id = call_args[1]['args'][0]
    reminder = Reminder.query.one()
    assert reminder.id == reminder_id
    assert call_args[1]['eta'] == notify_dt


def test_get_reminders_success(new_appointments):
    client = app.test_client()
    resp = client.get('/reminder')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert len(data['reminders']) == len(new_appointments)
    for reminder in data['reminders']:
        for field in REMINDER_FIELDS:
            assert field in reminder


def test_get_reminder_success(new_appointment):
    reminder_id = new_appointment.id
    db_session.add(new_appointment)
    db_session.commit()
    client = app.test_client()
    resp = client.get('/reminder/{}'.format(reminder_id))
    assert resp.status_code == 200
    details = json.loads(resp.data)
    for field in REMINDER_FIELDS:
        assert field in details


def test_delete_reminder_success(new_appointment):
    reminder_id = new_appointment.id
    db_session.add(new_appointment)
    db_session.commit()
    client = app.test_client()
    stored_reminder = Reminder.query.filter_by(id=reminder_id).one()
    assert stored_reminder is not None
    resp = client.delete('/reminder/{}'.format(reminder_id))
    assert resp.status_code == 200
    with pytest.raises(NoResultFound):
        Reminder.query.filter_by(id=reminder_id).one()


def test_inbound_handler_success(new_appointment):
    appt_id = new_appointment.id
    db_session.add(new_appointment)
    db_session.commit()
    client = app.test_client()
    inbound_req = {'to': 'myflowroutenumber',
                   'from': new_appointment.contact_num,
                   'body': 'Yes',
                   }
    resp = client.post('/', data=json.dumps(inbound_req),
                       content_type='application/json')
    assert resp.status_code == 200
    appt = Reminder.query.filter_by(id=appt_id).one()
    assert appt.has_confirmed is True


def test_inbound_handler_expired_appointment(new_appointment):
    pass
