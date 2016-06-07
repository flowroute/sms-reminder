import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm.exc import NoResultFound

from database import Base, db_session

from log import log


class Appointment(Base):
    """
    """
    __tablename__ = "appointment"
    id = Column(String(40), primary_key=True)
    contact_num = Column(String(18))
    appt_time = Column(DateTime)
    notify_time = Column(DateTime)
    has_confirmed = Column(Boolean, nullable=True, default=None)

    def __init__(self, contact_num, appt_time, notify_window):
        self.id = uuid.uuid4().hex
        self.contact_num = contact_num
        self.appt_time = datetime.utcnow()
        self.notify_time = datetime.utcnow()
