from flask import Flask
from appointment_reminder.settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, DEBUG_MODE, TEST_DB, DB
from appointment_reminder.database import init_db
from appointment_reminder import app


def configure_app(app=app):
    app.config.update(
        CELERY_BROKER_URL=CELERY_BROKER_URL,
        CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND)
    if DEBUG_MODE:
        app.debug = DEBUG_MODE
        app.config.update(SQLALCHEMY_DATABASE_URI='sqlite:///' + TEST_DB)
    else:
        app.config.update(SQLALCHEMY_DATABASE_URI='sqlite:///' + DB)
    init_db()
    return app


reminder_app = configure_app()

if __name__ == '__main__':
    import settings
    reminder_app.run(debug=settings.DEBUG_MODE)
