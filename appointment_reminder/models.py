import uuid
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm.exc import NoResultFound

from database import Base, db_session

from log import log


class Appointment(Base):
    """
    """
    @classmethod
    def clean_expired(cls):
        pass

    __tablename__ = "appointment"
    id = Column(String(40), primary_key=True)
    contact_num = Column(String(18))
    appt_dt = Column(DateTime)
    notify_dt = Column(DateTime)
    location = Column(String(128), nullable=True)
    participants = Column(String(256), nullable=True)
    has_confirmed = Column(Boolean, nullable=True, default=None)

    def __init__(self, contact_num, appt_dt, notify_win, location, participants):
        self.id = uuid.uuid4().hex
        self.contact_num = contact_num
        self.appt_dt = datetime.strptime(appt_dt, '%Y-%m-%d %H:%M')
        self.notify_dt = self.appt_dt - timedelta(hours=notify_win)
        self.location = location
        self.particpants = ', '.join(participants)
