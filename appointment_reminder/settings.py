# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from environs import Env

env = Env()
env.read_env()

FLOWROUTE_SECRET_KEY = env('FLOWROUTE_SECRET_KEY')
FLOWROUTE_ACCESS_KEY = env('FLOWROUTE_ACCESS_KEY')
FLOWROUTE_NUMBER = env('FLOWROUTE_NUMBER')

# Turn this to False when in production
is_debug = env('DEBUG_MODE', 'True')
if is_debug.lower() == 'true':
    DEBUG_MODE = True
else:
    DEBUG_MODE = False
# Default to INFO log level
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
SQLALCHEMY_TRACK_MODIFICATIONS = False

TEST_DB = "sqlite:///sqlite/test_appt_reminder.db"
DB = "sqlite:///sqlite/appt_reminder.db"

CELERY_BROKER_URL = env('CELERY_BROKER_URL',
                        'redis://localhost:6379')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND',
                            'redis://localhost:6379')
CELERY_ENABLE_UTC = True

# see arrow.locales for supported languages
LANGUAGE_DEFAULT = 'en_us'
ORG_NAME = env('ORG_NAME')

MSG_TEMPLATE = (u"[{}]\nYou have an appointment on {{}}{{}}. "
                u"Please reply 'Yes' to confirm, or 'No' "
                u"to cancel.").format(ORG_NAME)
LOCATION_OPERATOR = u"at"
PARTICIPANT_OPERATOR = u"with"
CONFIRMATION_RESPONSE = (u"[{}]\nThank you! Your appointment has been marked "
                         "confirmed.").format(ORG_NAME)
CANCEL_RESPONSE = (u"[{}]\nThank you! Your appointment has been"
                   u" marked canceled.").format(ORG_NAME)
UNPARSABLE_RESPONSE = (u"[{}]\nSorry, we did not understand your "
                       u"response. Please reply 'Yes' to confirm, or 'No' "
                       u"to cancel.").format(ORG_NAME)
