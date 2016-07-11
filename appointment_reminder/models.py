import uuid

import arrow
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm.exc import NoResultFound

from database import Base, db_session


class Reminder(Base):
    """
    """
    @classmethod
    def clean_expired(cls):
        current_ts = arrow.utcnow().datetime
        try:
            expired_reminders = db_session.query(cls).filter(
                cls.appt_sys_dt <= current_ts).all()
        except NoResultFound:
            return
        else:
            for reminder in expired_reminders:
                db_session.delete(reminder)
                db_session.commit()

    __tablename__ = "reminder"
    id = Column(String(40), primary_key=True)
    contact_num = Column(String(18), unique=True)
    appt_user_dt = Column(DateTime)
    appt_sys_dt = Column(DateTime)
    notify_sys_dt = Column(DateTime)
    location = Column(String(128), nullable=True)
    participant = Column(String(256), nullable=True)
    sms_sent = Column(Boolean, nullable=False, default=False)
    will_attend = Column(Boolean, nullable=True, default=None)

    def __init__(self, contact_num, appt_dt, notify_hrs_before, location,
                 participant):
        self.id = uuid.uuid4().hex
        self.contact_num = contact_num
        self.appt_user_dt = appt_dt.datetime
        self.appt_sys_dt = appt_dt.to('utc').datetime
        self.notify_sys_dt = appt_dt.to('utc').replace(
            hours=-notify_hrs_before).datetime
        self.location = location
        self.participant = participant
