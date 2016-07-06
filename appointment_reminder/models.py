import uuid

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm.exc import NoResultFound

from database import Base, db_session

from log import log


class Reminder(Base):
    """
    """
    @classmethod
    def clean_expired(cls):
        current_ts = pendulum.utcnow()
        try:
            expired_reminders = db_session.query(cls).filter(
                cls.appt_dt <= current_ts).all()
        except NoResultFound:
            return
        else:
            for reminder in expired_reminders:
                db_session.delete(reminder)
                db_session.commit()

    __tablename__ = "reminder"
    id = Column(String(40), primary_key=True)
    contact_num = Column(String(18))
    appt_dt = Column(DateTime)
    notify_dt = Column(DateTime)
    location = Column(String(128), nullable=True)
    participant = Column(String(256), nullable=True)
    has_confirmed = Column(Boolean, nullable=True, default=None)

    def __init__(self, contact_num, appt_dt, notify_win, location, participant):
        self.id = uuid.uuid4().hex
        self.contact_num = contact_num
        self.appt_dt = appt_dt
        self.notify_dt = self.appt_dt.to('utc').replace(hours=-notify_win)
        self.location = location
        self.participant = participant
