from flask import Flask
from celery import Celery

from settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, DEBUG_MODE, TEST_DB, DB
from database import init_db


def create_app():
    app = Flask(__name__)
    app.config.update(
        CELERY_BROKER_URL=CELERY_BROKER_URL,
        CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND)
    if DEBUG_MODE:
        app.debug = DEBUG_MODE
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + TEST_DB
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB
    init_db()
    return app


def new_celery(app):
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app = create_app()
celery = new_celery(app)


if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)
