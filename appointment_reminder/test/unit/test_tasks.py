# -*- coding: utf-8 -*-

import pytest
import mock
import arrow

from appointment_reminder.database import db_session
from appointment_reminder.tasks import (send_reminder, send_reply,
                                        create_message_body)
from appointment_reminder.settings import (TEST_DB, CONFIRMATION_RESPONSE,
                                           UNPARSABLE_RESPONSE)
from appointment_reminder.service import reminder_app as app
from appointment_reminder.models import Reminder


def teardown_module(function):
    db_session.rollback()
    if TEST_DB in app.config['SQLALCHEMY_DATABASE_URI']:
        Reminder.query.delete()
        db_session.commit()
    else:
        raise AttributeError(("The production database is turned on. "
                              "Flip settings.DEBUG to True"))


def setup_module(function):
    db_session.rollback()
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
    return reminder


@mock.patch('appointment_reminder.tasks.sms_controller')
def test_send_reminder(mock_sms_controller, new_reminder):
    db_session.add(new_reminder)
    db_session.commit()
    reminder_id = new_reminder.id
    send_reminder(reminder_id)
    assert mock_sms_controller.create_message.called == 1
    msg = mock_sms_controller.create_message.call_args[0][0].content
    assert msg == ("[Your Org Name]\nYou have an appointment on Monday Mar 23, "
                   "12:00 pm at Central Park with NY Running Club. Please "
                   "reply 'Yes' to confirm, or 'No' to cancel.")
    reminder = Reminder.query.filter_by(id=reminder_id).one()
    assert reminder.sms_sent is True


@pytest.mark.parametrize("num, confirm, content", [
    ('43332221111', True, CONFIRMATION_RESPONSE),
    ('08889996666', False, UNPARSABLE_RESPONSE),
])
@mock.patch('appointment_reminder.tasks.sms_controller')
def test_send_reply(mock_sms_controller, num, new_reminder, confirm, content):
    new_reminder.contact_num = num
    db_session.add(new_reminder)
    db_session.commit()
    reminder_id = new_reminder.id
    send_reply(reminder_id, confirm=confirm)
    assert mock_sms_controller.create_message.called is True
    msg = mock_sms_controller.create_message.call_args[0][0].content
    assert msg == content


def test_create_message(new_reminder):
    from appointment_reminder import tasks
    tasks.LANGUAGE_DEFAULT = 'ko_kr'
    new_reminder.contact_num = '122998778'
    db_session.add(new_reminder)
    db_session.commit()
    msg = create_message_body(new_reminder)
    assert msg == (u"[Your Org Name]\nYou have an appointment on"
                   u" \uc6d4\uc694\uc77c  3 23, 12:00  at Central Park with NY"
                   " Running Club. Please reply 'Yes' to confirm, "
                   "or 'No' to cancel.")
