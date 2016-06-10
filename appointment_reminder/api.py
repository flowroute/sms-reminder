import json

from flask import request, Response
from sqlalchemy.orm.exc import NoResultFound

from log import log
from app import app
from tasks import send_reminder
from database import db_session
from models import Reminder

# TODO add logging
# TODO add tz support
# TODO is grabbing the oldest reminder for a given customer good enough? Send a code with it?


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


class InvalidAPIUsage(Exception):
    """
    A generic exception for invalid API interactions.
    """
    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or())
        rv['message'] = self.message
        return rv


@app.route('/reminder', methods=['POST'])
def add_reminder():
    body = request.json
    try:
        contact_num = str(body['contact_number'])
        appt_dt = str(body['appointment_time'])
        notify_win = int(body['notify_window'])
        location = body.get('location', None)
        participants = body.get('participants', None)
    except KeyError:
        raise InvalidAPIUsage(
            ("Required arguments: 'contact_number' (str), "
             "'appointment_time' (str) eg. '2016-01-01 13:00', "
             "'notify_window' (int)"))
    appt = Reminder(contact_num, appt_dt, notify_win,
                    location, participants)
    db_session.add(appt)
    db_session.commit()
    send_reminder.apply_async(args=[appt.id], eta=appt.notify_dt)
    content = json.dumps({"message": ("successfully created new reminder, "
                          "and scheduled a SMS reminder."),
                          "appointment_id": appt.id})
    return Response(content, content_type="application/json")


@app.route('/reminder', methods=['GET'])
def get_reminders():
    reminders = Reminder.query.all()
    res = [{'reminder_id': rm.id, 'contact_number': rm.contact_num,
            'appt_datetime': rm.appt_dt, 'notify_at': rm.notify_dt,
            'has_confirmed': rm.has_confirmed, 'location': rm.location,
            'participants': rm.participants} for rm in reminders]
    return Response(json.dumps({"reminders": res}))


@app.route('/reminder/<uuid:reminder_id>', methods=['GET'])
def get_reminder(reminder_id):
    try:
        reminder = Reminder.query.filter_by(id=reminder_id).one()
    except NoResultFound:
        return Response(
            response=json.dumps({"message": "unknown reminder id"}),
            status_code=404, content_type='application/json')
    else:
        return Response(
            response=json.dumps(vars(reminder)),
            status_code=200, content_type='application/json')


@app.route('/reminder/<uuid:reminder_id>', methods=['DELETE'])
def remove_reminder(reminder_id):
    try:
        reminder = Reminder.query.filter_by(id=reminder_id).one()
    except NoResultFound:
        return Response(
            response=json.dumps({"message": "unknown reminder id"}),
            status_code=404, content_type='application/json')
    else:
        db_session.delete(reminder)
        db_session.commit()
        msg = {"message":
               "successfully deleted reminder {}".format(reminder_id)}
        return Response(response=json.dumps(msg), response_code=200,
                        content_type='application/json')


@app.route("/", methods=['POST'])
def inbound_handler():
    """
    The inbound request handler for consuming HTTP wrapped SMS content from
    Flowroute's messaging service.
    """
    body = request.json
    # Take the time to clear out any historical appointments.
    Reminder.clean_expired()
    try:
        virtual_tn = body['to']
        assert len(virtual_tn) <= 18
        sms_from = body['from']
        assert len(sms_from) <= 18
        message = body['body'].upper()
    except (TypeError, KeyError, AssertionError) as e:
        msg = ("Malformed inbound message: {}".format(body))
        log.error({"message": msg, "status": "failed", "exc": str(e)})
        return Response('There was an issue parsing your request.', status=400)
    else:
        appt = Reminder.query.filter_by(
            contact_num=sms_from, has_confirmed=None).order_by(
            Reminder.notify_dt.desc()).one()
        if 'YES' in message:
            appt.has_confirmed = True
        elif 'NO' in message:
            appt.has_confirmed = False
        db_session.add(appt)
        db_session.commit()
    return Response(status=200)
