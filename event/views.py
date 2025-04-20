from sqlalchemy.ext.asyncio import AsyncSession
from event.models import Event
from common.response import APIResponse
from event.schemas import EventCreate


async def create_event(event: EventCreate, db: AsyncSession):
    try:
        # Ensure end time is after start time
        if event.end_time <= event.start_time:
            return APIResponse.failure(message="End time must be after start time.", status_code=400)

        new_event = Event(
            name=event.name,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            max_attendees=event.max_attendees,
            status="scheduled"  # Initialized status
        )

        db.add(new_event)
        await db.commit()
        await db.refresh(new_event)

        return APIResponse.success(data={"event_id": new_event.event_id}, message="Event created successfully", status_code=201)

    except Exception as e:
        return APIResponse.failure(message="Failed to create event", data={"error": str(e)})
