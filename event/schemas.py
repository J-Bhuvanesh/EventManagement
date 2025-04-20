from typing import Optional, List
from pydantic import BaseModel, EmailStr
from event.models import EventStatusEnum
from datetime import datetime
from enum import Enum


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    max_attendees: int
    status: Optional[EventStatusEnum] = EventStatusEnum.scheduled


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    location: Optional[str]
    max_attendees: Optional[int]
    status: Optional[EventStatusEnum]


class AttendeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    event_id: int