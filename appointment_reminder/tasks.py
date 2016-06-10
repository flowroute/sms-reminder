from sqlalchemy.orm.exc import NoResultFound

from FlowrouteMessagingLib.Controllers.APIController import APIController
from FlowrouteMessagingLib.Models.Message import Message

from appointment_reminder.app import celery
from appointment_reminder.settings import (
    FLOWROUTE_ACCESS_KEY, FLOWROUTE_SECRET_KEY, FLOWROUTE_NUMBER,
    MSG_TEMPLATE, ORG_NAME)
from appointment_reminder.models import Reminder
from appointment_reminder.log import log


sms_controller = APIController(username=FLOWROUTE_ACCESS_KEY,
                               password=FLOWROUTE_SECRET_KEY)


def create_message_body(appt):
    appt_context = ''
    if appt.location:
        appt_context + ' at {}'.format(appt.location)
    if appt.participants:
        appt_context + ' with {}'.format(appt.participants)
    msg = MSG_TEMPLATE.format(ORG_NAME, appt.appt_dt, appt_context)
    return msg


@celery.task(name='tasks.send_reminder')
def send_reminder(appt_id):
    """
    """
    try:
        appt = Reminder.query.filter_by(id=appt_id).one()
    except NoResultFound:
        log.error({"message": "Received unknown appointment id.",
                   "status": "failed"})
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
                      "status": "failed",
                      "exc": e,
                      "strerr": strerr})
    else:
        log.info(
            {"message": "Message sent to {} for reminder {}".format(
             appt.contact_num, appt_id),
             "status": "succeeded"})
