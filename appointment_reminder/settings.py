import os

# Turn this to False when in production
DEBUG_MODE = os.environ.get('DEBUG_MODE', False)
# Default to INFO log level
LOG_LEVEL = os.environ.get('LOG_LEVEL', os.environ.get('LOG_LEVEL', 'INFO'))
SQLALCHEMY_TRACK_MODIFICATIONS = False


FLOWROUTE_SECRET_KEY = os.environ['FLOWROUTE_SECRET_KEY']
FLOWROUTE_ACCESS_KEY = os.environ['FLOWROUTE_ACCESS_KEY']
FLOWROUTE_NUMBER = os.environ['FLOWROUTE_NUMBER']


ORG_NAME = os.environ.get('ORG_NAME', 'Your Org Name')


TEST_DB = "sqlite:///test_appt_reminder.db"
DB = "sqlite:////var/lib/sqlite/data/appt_reminder.db"

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL',
                                   'redis://redis:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',
                                       'redis://redis:6379')
CELERY_ENABLE_UTC = True

MSG_TEMPLATE = ("[{}] You have an appointment on {{}}{{}}. "  # company, datetime, additional details
                "Please reply 'Yes' to confirm, or 'No' "
                "to cancel.").format(ORG_NAME)
CONFIRMATION_RESPONSE = ("[{}] Thank you! Your response has been "
                         "recorded.").format(ORG_NAME)
UNPARSABLE_RESPONSE = ("[{}] Sorry, we were unable to parse your response."
                       "Please reply 'Yes' to confirm, or 'No' "
                       "to cancel.").format(ORG_NAME)
