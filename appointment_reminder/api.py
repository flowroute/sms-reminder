# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from flask import request, Response
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import arrow
from arrow.parser import ParserError
from redis.exceptions import ConnectionError

from appointment_reminder.log import log
from appointment_reminder.tasks import send_reminder, send_reply
from appointment_reminder.database import db_session
from appointment_reminder.models import Reminder
from appointment_reminder import app


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
    """
    Adds a new reminder, and schedules an sms message handling celery task.
    If the redis is unavailable and unable to schedule a task the reminder
    is removed and an internal error is raised, otherwise the new reminder
    id is returned.

    Required:
    contact_number : string (The users phone number)
    appointment_time : string (The datetime of the appointment) "YYYY-MM-DDTHH:mmZ"
    notify_window : integer (The hours before the appointment to send reminder)

    Optional:
    location : string (Where the appointment is)
    participant : string (Who the appoinment is with)
    """
    body = request.json
    try:
        contact_num = str(body['contact_number'])
        appt_dt = arrow.get(body['appointment_time'], "YYYY-MM-DDTHH:mmZ")
        notify_win = int(body['notify_window'])
        location = body.get('location', None)
        participant = body.get('participant', None)
    except (KeyError, ParserError):
        raise InvalidAPIUsage(
            ("Required arguments: 'contact_number' (str), "
             "'appointment_time' (str) eg. '2016-01-01T13:00+02:00', "
             "'notify_window' (int)"))
    else:
        Reminder.clean_expired()
        reminder = Reminder(contact_num, appt_dt, notify_win,
                            location, participant)
        db_session.add(reminder)
    try:
        db_session.commit()
    except IntegrityError:
        msg = ("unable to create a new reminder. duplicate "
               "contact_number {}".format(contact_num))
        log.error({"message": msg})
        return Response(json.dumps({"message": msg}), status=400,
                        content_type="application/json")
    else:
        try:
            send_reminder.apply_async(args=[reminder.id],
                                      eta=reminder.notify_sys_dt)
        except ConnectionError as e:
            log.critical({"message": "unable to connect to redis",
                          "exc": type(e)})
            db_session.delete(reminder)
            db_session.commit()
            return Response(json.dumps(
                {"message": ("unable to create a new reminder."
                             " redis is unreachable"),
                 "exc": "RedisConnectionError"}),
                status=500, content_type="application/json")

        msg = "successfully created a reminder with id {}".format(reminder.id)
        log.info({"message": msg})
        content = json.dumps({"message": msg, "reminder_id": reminder.id})
        return Response(content, status=200,
                        content_type="application/json")


@app.route('/reminder', methods=['GET'])
def get_reminders():
    """
    Retrieves a list of all reminders
    """
    reminders = Reminder.query.all()
    res = [{'reminder_id': rm.id, 'contact_number': rm.contact_num,
            'appt_user_dt': str(rm.appt_user_dt), 'appt_sys_dt':
            str(rm.appt_sys_dt), 'notify_sys_dt': str(rm.notify_sys_dt),
            'will_attend': rm.will_attend, 'location': rm.location,
            'participant': rm.participant, 'reminder_sent': rm.reminder_sent,
            'confirm_sent': rm.confirm_sent}
           for rm in reminders]
    return Response(json.dumps({"reminders": res}), status=200,
                    content_type='application/json')


@app.route('/reminder/<reminder_id>', methods=['GET'])
def get_reminder(reminder_id):
    """
    Retrieves a specific reminder by id
    """
    try:
        rm = Reminder.query.filter_by(id=reminder_id).one()
    except NoResultFound:
        log.info({"message": "no reminder with id {}".format(reminder_id)})
        return Response(
            response=json.dumps({"message": "unknown reminder id"}),
            status=404, content_type='application/json')
    else:
        res = {'reminder_id': rm.id, 'contact_number': rm.contact_num,
               'appt_user_dt': str(rm.appt_user_dt), 'appt_sys_dt':
               str(rm.appt_sys_dt), 'notify_sys_dt': str(rm.notify_sys_dt),
               'will_attend': rm.will_attend, 'location': rm.location,
               'participant': rm.participant, 'reminder_sent': rm.reminder_sent,
               'confirm_sent': rm.confirm_sent}
        return Response(
            response=json.dumps(res),
            status=200, content_type='application/json')


@app.route('/reminder/<reminder_id>', methods=['DELETE'])
def remove_reminder(reminder_id):
    """
    The deletion route for Reminders - takes a reminder_id as an argument
    """
    try:
        reminder = Reminder.query.filter_by(id=reminder_id).one()
    except NoResultFound:
        log.info({"message": "no reminder with id {}".format(reminder_id)})
        return Response(
            response=json.dumps({"message": "unknown reminder id"}),
            status=404, content_type='application/json')
    else:
        db_session.delete(reminder)
        db_session.commit()
        msg = "successfully deleted reminder with id {}".format(reminder_id)
        log.info({"message": msg})
        return Response(
            response=json.dumps({"message": msg, "reminder_id": reminder_id}),
            status=200, content_type='application/json')


@app.route("/", methods=['POST'])
def inbound_handler():
    """
    The inbound request handler for consuming HTTP wrapped SMS content from
    Flowroute's messaging service.

    Validates proper message content, and takes time to clear the expired
    reminders before continuing. Retrieves the reminder based on the
    sender, and marks the 'will_attend' attribute according to whether
    there is 'yes' or 'no' (case insensitive) anywhere in the message.
    Responds to the user with a confirmation message and returns 200.
    """
    req = request.json
    # Take the time to clear out any past reminders
    try:
        virtual_tn = req['to']
        assert len(virtual_tn) <= 18
        sms_from = req['from']
        assert len(sms_from) <= 18
        req['body']
    except (TypeError, KeyError, AssertionError) as e:
        msg = ("Malformed inbound message: {}".format(req))
        log.error({"message": msg, "status": "failed", "exc": str(e)})
        return Response('There was an issue parsing your request.', status=400)
    else:
        Reminder.clean_expired()
        try:
            appt = Reminder.query.filter_by(
                contact_num=sms_from).one()
        except NoResultFound:
            msg = "no existing un-responded reminder for contact {}".format(
                sms_from)
            log.info({"message": msg})
            return Response(status=200)
        else:
            message = req['body'].upper()
            if 'YES' in message:
                appt.will_attend = True
                confirm = True
            elif 'NO' in message:
                appt.will_attend = False
                confirm = False
            else:
                confirm = None
            db_session.add(appt)
            try:
                send_reply.apply_async((appt.id,), {'confirm': confirm})
            except ConnectionError as e:
                log.critical({"message": "unable to connect to redis",
                              "exc": type(e)})
                db_session.rollback()
                return Response(status=500)
            else:
                db_session.commit()
                log.info({"message":
                          ("successfully recorded response from {}, scheduled "
                           "SMS confirmation for appointment {}").format(
                               sms_from, appt.id),
                          "reminder_id": appt.id})
                return Response(status=200)
