"""Check-in call service: the API the mobile app talks to, plus Twilio webhooks.

Run it with:  uvicorn app.main:create_app --factory --reload
"""

import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from . import voice
from .config import Settings
from .db import make_session_factory
from .deps import current_user, get_service, get_session
from .models import CheckIn, Contact, User
from .schemas import (
    AppCheckIn,
    CheckInOut,
    ContactCreate,
    ContactOut,
    ContactUpdate,
    RegisterOut,
    UserCreate,
    UserOut,
    UserUpdate,
)
from .service import CheckInService, new_token, next_checkin_at
from .telephony import ConsoleTelephony, Telephony, TwilioTelephony

log = logging.getLogger(__name__)


def user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        name=user.name,
        phone=user.phone,
        timezone=user.timezone,
        checkin_times=user.checkin_times,
        max_attempts=user.max_attempts,
        retry_minutes=user.retry_minutes,
        active=user.active,
        last_status=user.last_status,
        last_status_at=user.last_status_at,
        next_checkin_at=next_checkin_at(user),
    )


def create_app(
    settings: Settings | None = None,
    telephony: Telephony | None = None,
    session_factory: sessionmaker | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    session_factory = session_factory or make_session_factory(settings.database_url)
    if telephony is None:
        if settings.twilio_enabled:
            telephony = TwilioTelephony(
                settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_from_number
            )
        else:
            log.warning("Twilio is not configured: calls and SMS are only logged")
            telephony = ConsoleTelephony()
    service = CheckInService(session_factory, telephony, settings.public_base_url)

    async def scheduler_loop() -> None:
        while True:
            try:
                await asyncio.to_thread(service.tick)
            except Exception:
                log.exception("Scheduler tick failed")
            await asyncio.sleep(settings.scheduler_interval_seconds)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(scheduler_loop()) if settings.run_scheduler else None
        yield
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    app = FastAPI(title="Check-in Call Service", lifespan=lifespan)
    app.state.settings = settings
    app.state.session_factory = session_factory
    app.state.service = service
    app.state.telephony = telephony
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(voice.router)

    @app.get("/health")
    def health():
        return {"ok": True, "twilio": settings.twilio_enabled}

    # ------------------------------------------------------------ account

    @app.post("/users", response_model=RegisterOut, status_code=201)
    def register(body: UserCreate, s: Session = Depends(get_session)):
        if s.scalar(select(User.id).where(User.phone == body.phone)):
            raise HTTPException(status_code=409, detail="This phone number is already registered")
        user = User(
            name=body.name,
            phone=body.phone,
            timezone=body.timezone,
            max_attempts=body.max_attempts,
            retry_minutes=body.retry_minutes,
            api_token=new_token(),
        )
        user.checkin_times = body.checkin_times
        s.add(user)
        s.commit()
        return RegisterOut(user=user_out(user), api_token=user.api_token)

    @app.get("/me", response_model=UserOut)
    def get_me(user: User = Depends(current_user)):
        return user_out(user)

    @app.patch("/me", response_model=UserOut)
    def update_me(body: UserUpdate, user: User = Depends(current_user), s: Session = Depends(get_session)):
        for field, value in body.model_dump(exclude_unset=True).items():
            if value is None:
                continue
            setattr(user, field, value)
        s.commit()
        return user_out(user)

    @app.delete("/me", status_code=204)
    def delete_me(user: User = Depends(current_user), s: Session = Depends(get_session)):
        s.delete(user)
        s.commit()
        return Response(status_code=204)

    # ------------------------------------------------------------ contacts

    def own_contact(s: Session, user: User, contact_id: int) -> Contact:
        contact = s.get(Contact, contact_id)
        if contact is None or contact.user_id != user.id:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact

    @app.get("/me/contacts", response_model=list[ContactOut])
    def list_contacts(user: User = Depends(current_user)):
        return user.contacts

    @app.post("/me/contacts", response_model=ContactOut, status_code=201)
    def add_contact(body: ContactCreate, user: User = Depends(current_user), s: Session = Depends(get_session)):
        if len(user.contacts) >= 20:
            raise HTTPException(status_code=400, detail="At most 20 contacts")
        contact = Contact(user=user, **body.model_dump())
        s.add(contact)
        s.commit()
        return contact

    @app.patch("/me/contacts/{contact_id}", response_model=ContactOut)
    def update_contact(
        contact_id: int, body: ContactUpdate, user: User = Depends(current_user), s: Session = Depends(get_session)
    ):
        contact = own_contact(s, user, contact_id)
        for field, value in body.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(contact, field, value)
        s.commit()
        return contact

    @app.delete("/me/contacts/{contact_id}", status_code=204)
    def delete_contact(contact_id: int, user: User = Depends(current_user), s: Session = Depends(get_session)):
        s.delete(own_contact(s, user, contact_id))
        s.commit()
        return Response(status_code=204)

    # ------------------------------------------------------------ check-ins

    @app.get("/me/checkins", response_model=list[CheckInOut])
    def list_checkins(
        limit: int = Query(30, ge=1, le=200), user: User = Depends(current_user), s: Session = Depends(get_session)
    ):
        return s.scalars(
            select(CheckIn)
            .where(CheckIn.user_id == user.id)
            .order_by(CheckIn.scheduled_for.desc(), CheckIn.id.desc())
            .limit(limit)
        ).all()

    @app.post("/me/checkins", response_model=CheckInOut, status_code=201)
    def app_checkin(
        body: AppCheckIn,
        user: User = Depends(current_user),
        s: Session = Depends(get_session),
        service: CheckInService = Depends(get_service),
    ):
        checkin = service.record_app_checkin(s, user, body.status, body.note)
        s.commit()
        return checkin

    return app

