import pytest
import json


from appointment_reminder.settings import TEST_DB, DEBUG
from appointment_reminder.database import db_session
from appointment_reminder.models import Reminder
from appointment_reminder.app import app


def teardown_module(module):
    if TEST_DB in app.config['SQLALCHEMY_DATABASE_URI']:
        Reminder.query.delete()
        db_session.commit()
    else:
        raise AttributeError(("The production database is turned on. "
                              "Flip settings.DEBUG to True"))


def setup_module(module):
    if TEST_DB in app.config['SQLALCHEMY_DATABASE_URI']:
        Reminder.query.delete()
        db_session.commit()
    else:
        raise AttributeError(("The production database is turned on. "
                              "Flip settings.DEBUG to True"))


class MockController():
        def __init__(self):
            self.requests = []
            self.resp = []

        def create_message(self, msg):
            self.requests.append(msg)
            try:
                err = self.resp.pop(0)
            except:
                pass
            else:
                if err is False:
                    raise Exception("Unkown exception from FlowrouteSDK.")


@pytest.fixture
def mock_controller():
    return MockController()


@pytest.fixture
def appointment_details():
    content = {'contact_number': '12223334444',
               'appointment_time': '2020-01-01',
               'notify_window': '24',
               'location': 'Flowroute',
               'participant': 'Casey',
               }
    return content


def test_add_reminder(appointment_details):
    client = app.test_client()
    # TODO monkey patch the task method
    client.post('/reminder', data=json.dumps(appointment_details),
                content_type='application/json')
