from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from common.response import APIResponse
from event.models import Event, Registration, User, EventStatusEnum
from event.schemas import EventCreate, EventUpdate, AttendeeCreate
from sqlalchemy import select, func
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date



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


async def update_event(event_id: int, update_data: EventUpdate, db: AsyncSession):
    try:
        result = await db.execute(select(Event).where(Event.event_id == event_id))
        event = result.scalars().first()

        if not event:
            return APIResponse.failure(message="Event not found", status_code=404)

        if update_data.end_time and update_data.start_time and update_data.end_time <= update_data.start_time:
            return APIResponse.failure(message="End time must be after start time.", status_code=400)

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(event, field, value)

        await db.commit()
        await db.refresh(event)

        return APIResponse.success(message="Event updated successfully", data={"event_id": event.event_id})

    except Exception as e:
        return APIResponse.failure(message="Failed to update event", data={"error": str(e)})

async def update_event(event_id: int, update_data: EventUpdate, db: AsyncSession):
    try:
        result = await db.execute(select(Event).where(Event.event_id == event_id))
        event = result.scalars().first()

        if not event:
            return APIResponse.failure(message="Event not found", status_code=404)

        if update_data.end_time and update_data.start_time and update_data.end_time <= update_data.start_time:
            return APIResponse.failure(message="End time must be after start time.", status_code=400)

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(event, field, value)

        await db.commit()
        await db.refresh(event)

        return APIResponse.success(message="Event updated successfully", data={"event_id": event.event_id})

    except Exception as e:
        return APIResponse.failure(message="Failed to update event", data={"error": str(e)})



async def register_attendee(attendee_data: AttendeeCreate, db: AsyncSession):
    try:
        # 1. Fetch Event
        result = await db.execute(select(Event).where(Event.event_id == attendee_data.event_id))
        event = result.scalars().first()

        if not event:
            return APIResponse.failure(message="Event not found", status_code=404)
        if event.status == "completed":
            return APIResponse.failure(message="Event already completed", status_code=400)

        # 2. Check max attendees limit
        reg_count_result = await db.execute(
            select(func.count()).select_from(Registration).where(Registration.event_id == attendee_data.event_id)
        )
        if reg_count_result.scalar_one() >= event.max_attendees:
            return APIResponse.failure(message="Max attendee limit reached", status_code=400)

        # 3. Check or Create User
        user_result = await db.execute(select(User).where(User.email == attendee_data.email))
        user = user_result.scalars().first()

        if not user:
            user = User(
                first_name=attendee_data.first_name,
                last_name=attendee_data.last_name,
                email=attendee_data.email,
                phone_number=attendee_data.phone_number
            )
            db.add(user)
            await db.flush()  # Ensure user_id is available

        # 4. Check duplicate registration
        existing = await db.execute(
            select(Registration).where(
                Registration.user_id == user.user_id,
                Registration.event_id == attendee_data.event_id
            )
        )
        if existing.scalars().first():
            return APIResponse.failure(message="User already registered for this event", status_code=400)

        # 5. Create Registration
        registration = Registration(
            user_id=user.user_id,
            event_id=attendee_data.event_id,
            check_in_status=False
        )
        db.add(registration)
        await db.commit()
        await db.refresh(registration)

        return APIResponse.success(message="User registered successfully", data={"registration_id": registration.registration_id})

    except IntegrityError as e:
        await db.rollback()
        return APIResponse.failure(message="Integrity error", data={"error": str(e)}, status_code=400)
    except Exception as e:
        await db.rollback()
        return APIResponse.failure(message="Failed to register attendee", data={"error": str(e)})


async def list_events(status: Optional[EventStatusEnum], location: Optional[str], date: Optional[date], db: AsyncSession):
    try:
        query = select(Event)

        filters = []
        if status:
            filters.append(Event.status == status)
        if location:
            filters.append(Event.location == location)
        if date:
            filters.append(
                and_(
                    Event.start_time <= datetime.combine(date, datetime.max.time()),
                    Event.end_time >= datetime.combine(date, datetime.min.time())
                )
            )

        if filters:
            query = query.where(and_(*filters))

        result = await db.execute(query)
        events = result.scalars().all()

        return APIResponse.success(
            message="Filtered events fetched successfully",
            data=[{
                "event_id": e.event_id,
                "name": e.name,
                "start_time": e.start_time.isoformat() if e.start_time else None,
                "end_time": e.end_time.isoformat() if e.end_time else None,
                "location": e.location,
                "status": e.status
            } for e in events]
        )

    except Exception as e:
        return APIResponse.failure(message="Failed to list events", data={"error": str(e)})
