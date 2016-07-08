import os

DEBUG_MODE = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

FLOWROUTE_SECRET_KEY = os.environ.get('FLOWROUTE_SECRET_KEY', None)
FLOWROUTE_ACCESS_KEY = os.environ.get('FLOWROUTE_ACCESS_KEY', None)
FLOWROUTE_NUMBER = os.environ.get('FLOWROUTE_NUMBER', None)

ORG_NAME = os.environ.get('ORG_NAME', 'Your Org Name')


TEST_DB = "sqlite:///test_appt_reminder.db"
DB = "sqlite:////var/lib/sqlite/data/appt_reminder.db"

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL',
                                   'redis://redis:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',
                                       'redis://redis:6379')
CELERY_ENABLE_UTC = True

MSG_TEMPLATE = ("[{}] You have an appointment on {}{}. "  # company, datetime, additional details
                "Please reply 'Yes' to confirm, or 'No' "
                "to cancel.")
