from fastapi import APIRouter
import jwt
from datetime import datetime, timedelta

from common.config import Config
from common.response import APIResponse
from event.schemas import EventCreate
from event.views import create_event
from sqlalchemy.ext.asyncio import AsyncSession
from common.db import get_db
from fastapi import Depends

event_router = APIRouter(prefix="/api/v1/event", tags=["Events"])

# Simple test route
@event_router.post("/")
async def create_event_api(event: EventCreate, db: AsyncSession = Depends(get_db)):
    return await create_event(event,db)


@event_router.get("/generate-guest-token")
def generate_guest_token():
    payload = {
        "sub": "guest",
        "role": "guest",
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return APIResponse.success(data={"token": token}, message="Guest token generated")
