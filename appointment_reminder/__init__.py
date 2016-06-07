from flask import Flask

from settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


def create_app():
    app = Flask(__name__)
    app.config.update(
        CELERY_BROKER_URL=CELERY_BROKER_URL,
        CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
    )
