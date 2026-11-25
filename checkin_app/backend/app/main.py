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

from . import billing, voice
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
from .service import CheckInService, new_token, next_checkin_at, utcnow
from .telephony import ConsoleTelephony, Telephony, TwilioTelephony

log = logging.getLogger(__name__)


def user_out(user: User, require_subscription: bool) -> UserOut:
    now = utcnow()
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
        billing_id=user.billing_id,
        subscription_required=require_subscription,
        subscription_active=user.has_subscription(now),
        subscription_expires_at=user.subscription_expires_at if user.has_subscription(now) else None,
        subscription_will_renew=user.subscription_will_renew,
        calls_enabled=user.active and (not require_subscription or user.has_subscription(now)),
    )


def create_app(
    settings: Settings | None = None,
    telephony: Telephony | None = None,
    session_factory: sessionmaker | None = None,
    revenuecat: billing.RevenueCatClient | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    # Show this app's log lines (including the fake calls/texts) next to uvicorn's.
    app_log = logging.getLogger("app")
    if not app_log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
        app_log.addHandler(handler)
        app_log.setLevel(logging.INFO)
    session_factory = session_factory or make_session_factory(settings.database_url)
    if telephony is None:
        if settings.twilio_enabled:
            telephony = TwilioTelephony(
                settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_from_number
            )
        else:
            log.warning("Twilio is not configured: calls and SMS are only logged")
            telephony = ConsoleTelephony()
    service = CheckInService(
        session_factory, telephony, settings.public_base_url, require_subscription=settings.require_subscription
    )
    if revenuecat is None and settings.revenuecat_api_key:
        revenuecat = billing.RevenueCatClient(settings.revenuecat_api_key, settings.revenuecat_entitlement)
    if settings.require_subscription and revenuecat is None:
        log.warning("REQUIRE_SUBSCRIPTION is on but REVENUECAT_API_KEY is not set: purchases can't be confirmed")

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
    app.include_router(billing.make_router(settings, revenuecat))

    def out(user: User) -> UserOut:
        return user_out(user, settings.require_subscription)

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
            billing_id=new_token(),
        )
        user.checkin_times = body.checkin_times
        s.add(user)
        s.commit()
        return RegisterOut(user=out(user), api_token=user.api_token)

    @app.get("/me", response_model=UserOut)
    def get_me(user: User = Depends(current_user)):
        return out(user)

    @app.patch("/me", response_model=UserOut)
    def update_me(body: UserUpdate, user: User = Depends(current_user), s: Session = Depends(get_session)):
        for field, value in body.model_dump(exclude_unset=True).items():
            if value is None:
                continue
            setattr(user, field, value)
        s.commit()
        return out(user)

    @app.delete("/me", status_code=204)
    def delete_me(user: User = Depends(current_user), s: Session = Depends(get_session)):
        s.delete(user)
        s.commit()
        return Response(status_code=204)

    # ------------------------------------------------------------ subscription

    @app.post("/me/subscription/sync", response_model=UserOut)
    def sync_subscription(user: User = Depends(current_user), s: Session = Depends(get_session)):
        """Called by the app after a purchase or restore: re-checks the purchase with RevenueCat."""
        if revenuecat is not None:
            try:
                billing.apply_entitlement(user, revenuecat.fetch(user.billing_id))
            except Exception:
                log.exception("Could not check the subscription with RevenueCat")
                raise HTTPException(status_code=502, detail="Could not confirm the purchase, please try again")
            s.commit()
        return out(user)

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

