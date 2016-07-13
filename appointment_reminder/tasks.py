# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sqlalchemy.orm.exc import NoResultFound
from celery import Celery
import arrow

from FlowrouteMessagingLib.Controllers.APIController import APIController
from FlowrouteMessagingLib.Models.Message import Message

from appointment_reminder.settings import (
    FLOWROUTE_ACCESS_KEY, FLOWROUTE_SECRET_KEY, FLOWROUTE_NUMBER,
    MSG_TEMPLATE, CONFIRMATION_RESPONSE, UNPARSABLE_RESPONSE,
    LANGUAGE_DEFAULT)
from appointment_reminder.models import Reminder
from appointment_reminder.database import db_session
from appointment_reminder.log import log
from appointment_reminder.service import reminder_app

sms_controller = APIController(username=FLOWROUTE_ACCESS_KEY,
                               password=FLOWROUTE_SECRET_KEY)


def new_celery(app=reminder_app):
    celery = Celery(app.import_name)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = new_celery()


def create_message_body(appt):
    appt_context = u''
    if appt.location:
        appt_context += ' at {}'.format(appt.location)
    if appt.participant:
        appt_context += ' with {}'.format(appt.participant)
    msg = MSG_TEMPLATE.format(
        unicode(arrow.get(appt.appt_user_dt).format('dddd MMM DD, hh:mm a',
                                                    locale=LANGUAGE_DEFAULT)),
        appt_context)
    return msg


@celery.task(bind=True)
def send_reminder(self, reminder_id):
    """
    Retrieves the reminder from the database, passes message content to the
    Flowroute SMS client. If it fails, the task is re-queued.
    """
    try:
        appt = Reminder.query.filter_by(id=reminder_id).one()
    except NoResultFound:
        log.error(
            {"message": "Received unknown appointment with id {}.".format(
             reminder_id), "reminder_id": reminder_id})
        return
    msg_body = create_message_body(appt)
    message = Message(
        to=appt.contact_num,
        from_=FLOWROUTE_NUMBER,
        content=msg_body)
    try:
        sms_controller.create_message(message)
    except Exception as e:
        strerr = vars(e).get('response_body', None)
        log.critical({"message": "Raised an exception sending SMS",
                      "exc": e, "strerr": strerr, "reminder_id": reminder_id})
        raise self.retry(exc=e)
    else:
        log.info(
            {"message": "Reminder sent to {} for reminder_id {}".format(
             appt.contact_num, reminder_id),
             "reminder_id": reminder_id})
        appt.sms_sent = True
        db_session.add(appt)
        db_session.commit()


@celery.task(bind=True)
def send_reply(self, reminder_id, confirm=True):
    """
    Retrieves the remidner form the database, sends either a confirmation
    or a unparsable message response to the Flowroute SMS client. If it failes,
    the task is requeued.
    """
    try:
        appt = Reminder.query.filter_by(id=reminder_id).one()
    except NoResultFound:
        log.error(
            {"message": "Received unknown appointment with id {}.".format(
             reminder_id), "reminder_id": reminder_id})
        return
    if confirm:
        msg_content = CONFIRMATION_RESPONSE
    else:
        msg_content = UNPARSABLE_RESPONSE
    message = Message(
        to=appt.contact_num,
        from_=FLOWROUTE_NUMBER,
        content=msg_content)
    try:
        sms_controller.create_message(message)
    except Exception as e:
        strerr = vars(e).get('response_body', None)
        log.critical({"message": "Raised an exception sending SMS",
                      "exc": e, "strerr": strerr, "reminder_id": reminder_id})
        raise self.retry(exc=e)
    else:
        log.info(
            {"message": "Confirmation sent to {} for reminder_id {}".format(
             appt.contact_num, reminder_id),
             "reminder_id": reminder_id})
        appt.confirmation_sent = True
        db_session.add(appt)
        db_session.commit()
