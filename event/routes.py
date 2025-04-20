from typing import Optional
from fastapi import Query

from fastapi import APIRouter
import jwt
from datetime import datetime, timedelta,date

from common.config import Config
from common.response import APIResponse
from event.models import EventStatusEnum
from event.schemas import EventCreate, EventUpdate, AttendeeCreate
from event.views import create_event, update_event, register_attendee, list_events, bulk_check_in_attendees, \
    checkin_user
from sqlalchemy.ext.asyncio import AsyncSession
from common.db import get_db
from fastapi import Depends
from fastapi import Path

from fastapi import UploadFile, File


event_router = APIRouter(prefix="/api/v1/event", tags=["Events"])

# Simple test route
@event_router.post("/")
async def create_event_api(event: EventCreate, db: AsyncSession = Depends(get_db)):
    return await create_event(event,db)

@event_router.put("/{event_id}")
async def update_event_api(
        update_data: EventUpdate,
        event_id: int = Path(...),
    db: AsyncSession = Depends(get_db)
):
    return await update_event(event_id, update_data, db)



@event_router.post("/register")
async def register_attendee_api(
    attendee_data: AttendeeCreate,
    db: AsyncSession = Depends(get_db)
):
    return await register_attendee(attendee_data, db)


@event_router.get("/")
async def get_event_api(
    status: Optional[EventStatusEnum] = Query(None),
    location: Optional[str] = Query(None),
    date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await list_events(status=status, location=location, date=date, db=db)

@event_router.post("/{event_id}/bulk-checkin")
async def bulk_checkin(
    event_id: int = Path(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    return await bulk_check_in_attendees(event_id=event_id, file=file, db=db)
@event_router.post("/{event_id}/checkin/{user_id}")
async def checkin_user_api(event_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    return await checkin_user(event_id=event_id, user_id=user_id, db=db)

@event_router.get("/generate-guest-token")
def generate_guest_token():
    payload = {
        "sub": "guest",
        "role": "guest",
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return APIResponse.success(data={"token": token}, message="Guest token generated")
