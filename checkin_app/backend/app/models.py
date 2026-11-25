"""Database tables.

All datetimes are stored as naive UTC.
"""

import json
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

# User.last_status / CheckIn.status values
UNKNOWN = "unknown"
PENDING = "pending"  # waiting for the next call attempt
CALLING = "calling"  # a call is in progress
OK = "ok"
NEEDS_HELP = "needs_help"
MISSED = "missed"  # no answer after every attempt

# CheckIn.escalation_status values
ESC_IN_PROGRESS = "in_progress"
ESC_ACKNOWLEDGED = "acknowledged"  # a contact pressed 1 to say they'll handle it
ESC_EXHAUSTED = "exhausted"  # every contact was called, nobody acknowledged
ESC_CANCELLED = "cancelled"  # the user checked in OK afterwards
ESC_NO_CONTACTS = "no_contacts"

# Alert.status values
ALERT_QUEUED = "queued"
ALERT_CALLING = "calling"
ALERT_ACKNOWLEDGED = "acknowledged"
ALERT_NO_ANSWER = "no_answer"
ALERT_CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    checkin_times_json: Mapped[str] = mapped_column(String(500), default='["09:00"]')
    max_attempts: Mapped[int] = mapped_column(default=3)
    retry_minutes: Mapped[int] = mapped_column(default=10)
    active: Mapped[bool] = mapped_column(default=True)
    api_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    last_status: Mapped[str] = mapped_column(String(20), default=UNKNOWN)
    last_status_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    # In-app purchase. billing_id is the customer id the app gives RevenueCat; it is random
    # (not the user id) so a deleted account's purchases can never pass to a new account.
    billing_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    subscription_expires_at: Mapped[datetime | None] = mapped_column(default=None)
    subscription_product: Mapped[str | None] = mapped_column(String(100), default=None)
    subscription_will_renew: Mapped[bool] = mapped_column(default=False)

    def has_subscription(self, now: datetime) -> bool:
        return self.subscription_expires_at is not None and self.subscription_expires_at > now

    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", order_by="Contact.priority"
    )
    checkins: Mapped[list["CheckIn"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @property
    def checkin_times(self) -> list[str]:
        return json.loads(self.checkin_times_json)

    @checkin_times.setter
    def checkin_times(self, times: list[str]) -> None:
        self.checkin_times_json = json.dumps(sorted(set(times)))


class Contact(Base):
    """Someone to alert: family, a caregiver, a hospital or clinic, a neighbour..."""

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    relation: Mapped[str] = mapped_column(String(20), default="family")
    priority: Mapped[int] = mapped_column(default=1)  # 1 is called first
    notify_sms: Mapped[bool] = mapped_column(default=True)
    notify_call: Mapped[bool] = mapped_column(default=True)

    user: Mapped[User] = relationship(back_populates="contacts")


class CheckIn(Base):
    """One scheduled check-in (or one the user made from the app)."""

    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("user_id", "slot_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source: Mapped[str] = mapped_column(String(10), default="call")  # "call" or "app"
    # Local date + time of the scheduled slot, e.g. "2026-11-25T09:00". None for app check-ins.
    slot_key: Mapped[str | None] = mapped_column(String(20), default=None)
    scheduled_for: Mapped[datetime] = mapped_column(default=utcnow)
    status: Mapped[str] = mapped_column(String(20), default=PENDING, index=True)
    attempts: Mapped[int] = mapped_column(default=0)
    next_attempt_at: Mapped[datetime | None] = mapped_column(default=None, index=True)
    call_started_at: Mapped[datetime | None] = mapped_column(default=None)
    call_sid: Mapped[str | None] = mapped_column(String(64), default=None)
    note: Mapped[str | None] = mapped_column(String(500), default=None)
    completed_at: Mapped[datetime | None] = mapped_column(default=None)
    escalation_status: Mapped[str | None] = mapped_column(String(20), default=None, index=True)

    user: Mapped[User] = relationship(back_populates="checkins")
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="checkin", cascade="all, delete-orphan", order_by="Alert.position"
    )


class Alert(Base):
    """One contact being notified about one check-in."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    checkin_id: Mapped[int] = mapped_column(ForeignKey("checkins.id"), index=True)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"))
    contact_name: Mapped[str] = mapped_column(String(100))
    contact_phone: Mapped[str] = mapped_column(String(20))
    position: Mapped[int] = mapped_column(default=0)
    call: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(String(20), default=ALERT_QUEUED)
    sms_sent: Mapped[bool] = mapped_column(default=False)
    call_sid: Mapped[str | None] = mapped_column(String(64), default=None)
    call_started_at: Mapped[datetime | None] = mapped_column(default=None)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow)

    checkin: Mapped[CheckIn] = relationship(back_populates="alerts")
