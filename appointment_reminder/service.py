from flask import Flask
from sqlalchemy.exc import OperationalError

from appointment_reminder.settings import DEBUG_MODE, TEST_DB, DB
from appointment_reminder.database import init_db, destroy_db
from appointment_reminder import app
from appointment_reminder.log import log


def configure_app(app=app):
    if DEBUG_MODE:
        try:
            destroy_db()
        except OperationalError:
            log.info({"message": "nothing to destroy, table doesn't exist"})
        app.debug = DEBUG_MODE
        app.config.update(SQLALCHEMY_DATABASE_URI=TEST_DB)
    else:
        app.config.update(SQLALCHEMY_DATABASE_URI=DB)
    try:
        init_db()
    except OperationalError:
        log.info({"message": "database already exists... moving on."})
    return app


reminder_app = configure_app()
