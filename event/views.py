from typing import Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from common.db import get_db
from common.response import APIResponse
from event.models import Event, Registration, User, EventStatusEnum
from event.schemas import EventCreate, EventUpdate, AttendeeCreate
from sqlalchemy import select, func
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date

import csv
from io import StringIO

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


async def run_auto_complete():
    try:
        # Ensure that the database session is correctly managed within async context
        async for db in get_db():
            # Your logic to auto-complete past events
            result = await db.execute(select(Event).where(Event.end_time < datetime.utcnow()))
            events_to_update = result.scalars().all()

            for event in events_to_update:
                event.status = EventStatusEnum.completed
                await db.commit()

            print(f"Auto-completed {len(events_to_update)} past events.")
    except Exception as e:
        print(f"Error during auto-completion: {e}")

async def checkin_user(event_id: int, user_id: int, db: AsyncSession):
    try:
        # Fetch the event
        event_result = await db.execute(select(Event).where(Event.event_id == event_id))
        event = event_result.scalars().first()

        if not event:
            return APIResponse.failure(message="Event not found", status_code=404)

        # Fetch the user
        user_result = await db.execute(select(User).where(User.user_id == user_id))
        user = user_result.scalars().first()

        if not user:
            return APIResponse.failure(message="User not found", status_code=404)

        # Check if the user is registered for the event
        registration_result = await db.execute(
            select(Registration).where(
                Registration.event_id == event_id,
                Registration.user_id == user_id
            )
        )
        registration = registration_result.scalars().first()

        if not registration:
            return APIResponse.failure(message="User is not registered for this event", status_code=404)

        # Mark the user as checked in
        registration.check_in_status = True
        await db.commit()
        await db.refresh(registration)

        return APIResponse.success(message="User checked in successfully", data={"user_id": user_id, "event_id": event_id})

    except Exception as e:
        return APIResponse.failure(message="Failed to check-in user", data={"error": str(e)})

async def bulk_check_in_attendees(event_id: int, file: UploadFile, db: AsyncSession):
    try:
        # Only allow CSV files
        if file.content_type != "text/csv":
            return APIResponse.failure(message="Only CSV files are allowed", status_code=400)

        # Read and decode CSV file content
        content = await file.read()
        csv_data = content.decode("utf-8")
        csv_reader = csv.DictReader(StringIO(csv_data))

        checked_in_users = []
        event = await db.execute(select(Event).where(Event.event_id == event_id))
        event = event.scalars().first()

        if not event:
            return APIResponse.failure(message="Event not found", status_code=404)

        # Check if max attendees limit has been reached
        count_result = await db.execute(
            select(func.count()).select_from(Registration).where(Registration.event_id == event_id)
        )
        current_count = count_result.scalar_one()

        if current_count >= event.max_attendees:
            return APIResponse.failure(message="Max attendee limit reached", status_code=400)

        for row in csv_reader:
            email = row.get("email")
            phone = row.get("phone_number")

            if not email and not phone:
                continue  # Skip rows without valid identification

            # Fetch user by email or phone number
            user_query = select(User).where(
                (User.email == email) if email else (User.phone_number == phone)
            )
            user_result = await db.execute(user_query)
            user = user_result.scalars().first()

            # If user doesn't exist, create a new user
            if not user:
                user_data = {
                    "first_name": row.get("first_name"),
                    "last_name": row.get("last_name"),
                    "email": email,
                    "phone_number": phone
                }

                user = User(**user_data)
                db.add(user)
                await db.commit()
                await db.refresh(user)

            # Check if user is already registered for the event
            reg_query = select(Registration).where(
                Registration.event_id == event_id,
                Registration.user_id == user.user_id
            )
            reg_result = await db.execute(reg_query)
            registration = reg_result.scalars().first()

            # If user is not registered, create a registration
            if not registration:
                registration = Registration(
                    user_id=user.user_id,
                    event_id=event_id,
                    check_in_status=False
                )
                db.add(registration)

            registration.check_in_status = True
            checked_in_users.append(user.email or user.phone_number)

        await db.commit()

        return APIResponse.success(
            message="Bulk check-in completed",
            data={"checked_in": checked_in_users}
        )

    except Exception as e:
        return APIResponse.failure(message="Failed to process CSV check-in", data={"error": str(e)})