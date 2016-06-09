import os

DEBUG_MODE = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

FLOWROUTE_SECRET_KEY = os.environ.get('FLOWROUTE_SECRET_KEY', None)
FLOWROUTE_ACCESS_KEY = os.environ.get('FLOWROUTE_ACCESS_KEY', None)
FLOWROUTE_NUMBER = os.environ.get('FLOWROUTE_NUMBER', None)

ORG_NAME = os.environ.get('ORG_NAME', 'Your Org Name')


TEST_DB = "test_appt_reminder.db"
DB = "appt_reminder.db"

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL',
                                   'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',
                                       'redis://localhost:6379')

MSG_TEMPLATE = ("Greetings from {}. This a reminder for your {} " # company, datetime
                "appointment{}. Please reply 'Yes' to confirm, or 'No' "
                "to cancel this appointment.")  # if location, at location, if participants, with particpants
