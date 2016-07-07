from flask import Flask

from appointment_reminder.settings import (CELERY_BROKER_URL,
                                           CELERY_RESULT_BACKEND,
                                           CELERY_ENABLE_UTC)


app = Flask(__name__)
app.config.update(
        BROKER_URL=CELERY_BROKER_URL,
        CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
        CELERY_ENABLE_UTC=CELERY_ENABLE_UTC)
import appointment_reminder.api
