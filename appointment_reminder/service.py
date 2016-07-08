from flask import Flask

from appointment_reminder.settings import DEBUG_MODE, TEST_DB, DB
from appointment_reminder.database import init_db
from appointment_reminder import app


def configure_app(app=app):
    if DEBUG_MODE:
        app.debug = DEBUG_MODE
        app.config.update(SQLALCHEMY_DATABASE_URI=TEST_DB)
    else:
        app.config.update(SQLALCHEMY_DATABASE_URI=DB)
    init_db()
    return app


reminder_app = configure_app()

if __name__ == '__main__':
    reminder_app.run(debug=DEBUG_MODE)
