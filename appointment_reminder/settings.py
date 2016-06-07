import os

DEBUG_MODE = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

FLOWROUTE_SECRET_KEY = os.environ.get('FLOWROUTE_SECRET_KEY', None)
FLOWROUTE_ACCESS_KEY = os.environ.get('FLOWROUTE_ACCESS_KEY', None)

ORG_NAME = os.environ.get('ORG_NAME', 'Your Org Name')


TEST_DB = "test_sms_proxy.db"
DB = "sms_proxy.db"

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL',
                                   'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',
                                       'redis://localhost:6379')
