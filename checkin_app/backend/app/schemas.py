import re
from datetime import datetime, timezone
from typing import Annotated, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AfterValidator, BaseModel, Field, PlainSerializer, field_validator

E164 = re.compile(r"^\+[1-9]\d{6,14}$")
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

# Times are stored as naive UTC; send them with a "Z" so phones convert them correctly.
UTC = Annotated[
    datetime,
    PlainSerializer(lambda d: d.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"), return_type=str),
]


def _check_phone(value: str) -> str:
    cleaned = re.sub(r"[\s\-().]", "", value)
    if not E164.match(cleaned):
        raise ValueError("phone must be in international format, e.g. +14155550123")
    return cleaned


Phone = Annotated[str, AfterValidator(_check_phone)]
Relation = Literal["family", "friend", "caregiver", "doctor", "hospital", "neighbor", "other"]


def _check_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError("unknown timezone, use a name like 'America/New_York'")
    return value


def _check_times(values: list[str]) -> list[str]:
    for value in values:
        if not HHMM.match(value):
            raise ValueError(f"'{value}' is not a 24-hour HH:MM time")
    return sorted(set(values))


class ScheduleFields(BaseModel):
    @field_validator("timezone", check_fields=False)
    @classmethod
    def _tz(cls, v):
        return v if v is None else _check_timezone(v)

    @field_validator("checkin_times", check_fields=False)
    @classmethod
    def _times(cls, v):
        return v if v is None else _check_times(v)


class UserCreate(ScheduleFields):
    name: str = Field(min_length=1, max_length=100)
    phone: Phone
    timezone: str = "UTC"
    checkin_times: list[str] = Field(default_factory=lambda: ["09:00"], max_length=24)
    max_attempts: int = Field(3, ge=1, le=10)
    retry_minutes: int = Field(10, ge=1, le=240)


class UserUpdate(ScheduleFields):
    name: str | None = Field(None, min_length=1, max_length=100)
    timezone: str | None = None
    checkin_times: list[str] | None = Field(None, max_length=24)
    max_attempts: int | None = Field(None, ge=1, le=10)
    retry_minutes: int | None = Field(None, ge=1, le=240)
    active: bool | None = None


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    timezone: str
    checkin_times: list[str]
    max_attempts: int
    retry_minutes: int
    active: bool
    last_status: str
    last_status_at: UTC | None
    next_checkin_at: UTC | None
    billing_id: str
    subscription_required: bool
    subscription_active: bool
    subscription_expires_at: UTC | None
    subscription_will_renew: bool
    # False when paused or when a subscription is required and missing.
    calls_enabled: bool


class RegisterOut(BaseModel):
    user: UserOut
    api_token: str


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: Phone
    relation: Relation = "family"
    priority: int = Field(1, ge=1, le=99)
    notify_sms: bool = True
    notify_call: bool = True


class ContactUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    phone: Phone | None = None
    relation: Relation | None = None
    priority: int | None = Field(None, ge=1, le=99)
    notify_sms: bool | None = None
    notify_call: bool | None = None


class ContactOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    phone: str
    relation: str
    priority: int
    notify_sms: bool
    notify_call: bool


class AppCheckIn(BaseModel):
    status: Literal["ok", "needs_help"]
    note: str | None = Field(None, max_length=500)


class AlertOut(BaseModel):
    model_config = {"from_attributes": True}

    contact_name: str
    status: str
    sms_sent: bool


class CheckInOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    source: str
    scheduled_for: UTC
    status: str
    attempts: int
    note: str | None
    completed_at: UTC | None
    escalation_status: str | None
    alerts: list[AlertOut]
