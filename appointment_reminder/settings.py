# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

FLOWROUTE_SECRET_KEY = os.environ['FLOWROUTE_SECRET_KEY']
FLOWROUTE_ACCESS_KEY = os.environ['FLOWROUTE_ACCESS_KEY']
FLOWROUTE_NUMBER = os.environ['FLOWROUTE_NUMBER']

# Turn this to False when in production
is_debug = os.environ.get('DEBUG_MODE', 'false')
if is_debug.lower() == 'true':
    DEBUG_MODE = True
else:
    DEBUG_MODE = False
# Default to INFO log level
LOG_LEVEL = os.environ.get('LOG_LEVEL', os.environ.get('LOG_LEVEL', 'INFO'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

TEST_DB = "sqlite:////var/lib/sqlite/data/test_appt_reminder.db"
DB = "sqlite:////var/lib/sqlite/data/appt_reminder.db"

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL',
                                   'redis://redis:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',
                                       'redis://redis:6379')
CELERY_ENABLE_UTC = True

# see arrow.locales for supported languages
LANGUAGE_DEFAULT = 'en_us'
ORG_NAME = os.environ.get('ORG_NAME', 'Your Org Name')

MSG_TEMPLATE = (u"[{}]\nYou have an appointment on {{}}{{}}. "
                u"Please reply 'Yes' to confirm, or 'No' "
                u"to cancel.").format(ORG_NAME)
LOCATION_OPERATOR = u"at"
PARTICIPANT_OPERATOR = u"with"
CONFIRMATION_RESPONSE = (u"[{}]\nThank you! Your appointment has been marked "
                         "confirmed.").format(ORG_NAME)
CANCEL_RESPONSE = (u"[{}]\nThank you! Your appointment has been"
                   u" marked canceled.").format(ORG_NAME)
UNPARSABLE_RESPONSE = (u"[{}]\nSorry, we were unable to parse your response. "
                       u"Please reply 'Yes' to confirm, or 'No' "
                       u"to cancel.").format(ORG_NAME)
