from flask import Flask
import sqlite3 as sqlite

from appointment_reminder.settings import DEBUG_MODE, TEST_DB, DB
from appointment_reminder.database import init_db, destroy_db
from appointment_reminder import app
from appointment_reminder.log import log


def configure_app(app=app):
    if DEBUG_MODE:
        destroy_db()
        app.debug = DEBUG_MODE
        app.config.update(SQLALCHEMY_DATABASE_URI=TEST_DB)
    else:
        app.config.update(SQLALCHEMY_DATABASE_URI=DB)
    try:
        init_db()
    except sqlite.OperationalError:
        log.info({"message": "database already exists... moving on."})
    return app


reminder_app = configure_app()

if __name__ == '__main__':
    reminder_app.run(debug=DEBUG_MODE)
