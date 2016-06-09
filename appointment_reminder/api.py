import json

from flask import request, Response

from log import log
from app import app
from tasks import send_reminder
from database import db_session
from models import Appointment


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


@app.route('/appointment', methods=['POST'])
def add_appointment():
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
    appt = Appointment(contact_num, appt_dt, notify_win,
                       location, participants)
    db_session.add(appt)
    db_session.commit()
    send_reminder.apply_async(args=[appt.id], eta=appt.notify_dt)
    content = json.dumps({"message": ("Successfully created new appointment, "
                          "and scheduled a SMS reminder."),
                          "appointment_id": appt.id})
    return Response(content, content_type="application/json")


@app.route("/", methods=['POST'])
def inbound_handler():
    """
    The inbound request handler for consuming HTTP wrapped SMS content from
    Flowroute's messaging service.
    """
    body = request.json
    # Take the time to clear out any historical appointments.
    Appointment.clean_expired()
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
        appts = Appointment.query.filter_by(contact_num=sms_from).order_by(
            Appointment.notify_dt.desc()).all()
        for appt in appts:
            if appt.has_confirmed is None:
                if 'YES' in message:
                    appt.has_confirmed = True
                elif 'NO' in message:
                    appt.has_confirmed = False
                db_session.add(appt)
                db_session.commit()
                break
    return Response(status=200)
