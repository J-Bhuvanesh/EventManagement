from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum

from common.db import Base


class EventStatusEnum(str, enum.Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String, nullable=False)

    registrations = relationship("Registration", back_populates="user")


class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String)
    max_attendees = Column(Integer, nullable=False)
    status = Column(Enum(EventStatusEnum), default=EventStatusEnum.scheduled)

    registrations = relationship("Registration", back_populates="event")


class Registration(Base):
    __tablename__ = "registrations"

    registration_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.event_id"), nullable=False)
    check_in_status = Column(Boolean, default=False)

    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
