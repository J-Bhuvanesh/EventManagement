from fastapi import APIRouter
import jwt
from datetime import datetime, timedelta

from common.config import Config
from common.response import APIResponse
from event.schemas import EventCreate, EventUpdate, AttendeeCreate
from event.views import create_event, update_event, register_attendee
from sqlalchemy.ext.asyncio import AsyncSession
from common.db import get_db
from fastapi import Depends
from fastapi import Path


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




@event_router.get("/generate-guest-token")
def generate_guest_token():
    payload = {
        "sub": "guest",
        "role": "guest",
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return APIResponse.success(data={"token": token}, message="Guest token generated")
