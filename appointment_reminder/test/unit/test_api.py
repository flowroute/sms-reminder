import pytest
import json
import mock
import arrow
from sqlalchemy.orm.exc import NoResultFound

from appointment_reminder.settings import TEST_DB
from appointment_reminder.database import db_session
from appointment_reminder.models import Reminder
from appointment_reminder.service import reminder_app as app


def teardown_module(function):
    if TEST_DB in app.config['SQLALCHEMY_DATABASE_URI']:
        db_session.rollback()
        Reminder.query.delete()
        db_session.commit()
    else:
        raise AttributeError(("The production database is turned on. "
                              "Flip settings.DEBUG to True"))


def setup_function(function):
    if TEST_DB in app.config['SQLALCHEMY_DATABASE_URI']:
        db_session.rollback()
        Reminder.query.delete()
        db_session.commit()
    else:
        raise AttributeError(("The production database is turned on. "
                              "Flip settings.DEBUG to True"))

REMINDER_FIELDS = ('contact_number', 'participant', 'reminder_id',
                   'appt_user_dt', 'appt_sys_dt', 'location', 'will_attend',
                   'notify_sys_dt', 'reminder_sent', 'confirm_sent')


@pytest.fixture
def appointment_details():
    content = {'contact_number': '12223334444',
               'appointment_time': '2020-01-01T13:00+0300',
               'notify_window': '24',
               'location': 'Flowroute',
               'participant': 'Casey',
               }
    return content


@pytest.fixture
def new_appointment():
    contact = '1222333555'
    appt_str_time_0 = '2030-01-01T13:00+0000'
    notify_win = 24
    location = 'Flowroute HQ'
    participant_0 = 'Development Teams'
    reminder = Reminder(contact, arrow.get(appt_str_time_0), notify_win,
                        location, participant_0)
    return reminder


@pytest.fixture
def new_appointments(new_appointment):
    contact_0 = '12223334444'
    appt_str_time_0 = '2016-01-01T13:00+0700'
    notify_win = 24
    location = 'Family Physicians'
    participant_0 = 'Dr Smith'
    reminder_0 = Reminder(contact_0, arrow.get(appt_str_time_0), notify_win,
                          location, participant_0)
    appt_str_time_1 = '2020-01-01T13:00+0000'
    participant_1 = 'Dr Martinez'
    contact_1 = '12223335555'
    reminder_1 = Reminder(contact_1, arrow.get(appt_str_time_1), notify_win,
                          location, participant_1)
    db_session.add(reminder_0)
    db_session.add(new_appointment)
    db_session.commit()
    db_session.add(reminder_1)
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
    dt = arrow.get(reminder_time, "YYYY-MM-DDTHH:mmZ")
    notify_sys_dt = dt.replace(hours=-int(
        appointment_details['notify_window']))
    reminder_id = call_args[1]['args'][0]
    reminder = Reminder.query.one()
    assert reminder.id == reminder_id
    assert arrow.get(call_args[1]['eta']) == notify_sys_dt


@mock.patch('appointment_reminder.api.send_reminder')
def test_add_reminder_unique_constraint(mock_send_reminder, new_appointment,
                                        appointment_details):
    client = app.test_client()
    db_session.add(new_appointment)
    db_session.commit()
    dup_num = new_appointment.contact_num
    appointment_details['contact_number'] = dup_num
    resp = client.post('/reminder', data=json.dumps(appointment_details),
                       content_type='application/json')
    data = json.loads(resp.data)
    assert data['message'] == ("unable to create a new reminder. duplicate "
                               "contact_number {}".format(dup_num))
    assert resp.status_code == 400


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

@pytest.mark.parametrize("response, status", [
    ('Yes', True),
    ('YES', True),
    ('yes i will be there', True),
    ('No', False),
    ('NO', False),
    ('no i need to cancel', False)

])
@mock.patch('appointment_reminder.api.send_reply')
def test_inbound_handler_success(mock_send_reply, new_appointment,
                                 response, status):
    appt_id = new_appointment.id
    db_session.add(new_appointment)
    db_session.commit()
    client = app.test_client()
    inbound_req = {'to': 'myflowroutenumber',
                   'from': new_appointment.contact_num,
                   'body': response,
                   }
    resp = client.post('/', data=json.dumps(inbound_req),
                       content_type='application/json')
    assert mock_send_reply.apply_async.called == 1
    assert resp.status_code == 200
    appt = Reminder.query.filter_by(id=appt_id).one()
    assert appt.will_attend is status


@mock.patch('appointment_reminder.api.send_reply')
def test_inbound_handler_expired_appointment(mock_send_reply, appointment_details):
    contact_0 = '12223333333'
    contact_1 = '12229991111'
    appt_str_time_0 = '2000-01-01T13:00+0000'
    appt_str_time_1 = '2020-01-01T12:00+0000'
    notify_win = 24
    location = 'Flowroute HQ'
    participant_0 = 'Development Teams'
    reminder_0 = Reminder(contact_0, arrow.get(appt_str_time_0), notify_win,
                          location, participant_0)
    reminder_1 = Reminder(contact_1, arrow.get(appt_str_time_1),
                          notify_win, location, participant_0)
    db_session.add(reminder_0)
    db_session.add(reminder_1)
    db_session.commit()
    client = app.test_client()
    inbound_req = {'to': 'myflowroutenumber',
                   'from': reminder_1.contact_num,
                   'body': 'Yes'}
    resp = client.post('/', data=json.dumps(inbound_req),
                       content_type='application/json')
    reminders = Reminder.query.all()
    assert mock_send_reply.apply_async.called is True
    assert len(reminders) == 1
    reminders[0].contact_num == contact_1
    assert resp.status_code == 200
