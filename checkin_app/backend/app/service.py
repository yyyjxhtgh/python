"""Check-in logic.

The scheduler calls `tick()` every ~30 seconds. Each tick:

1. Gives up on calls that never reported back (counted as "no answer").
2. Creates a check-in for every scheduled time that has just arrived.
3. Calls users whose check-in is due (first try or a retry).
4. Moves escalations along: calls the next contact when the previous one
   didn't answer or didn't press 1.

Twilio webhooks feed results back in through `record_checkin_response`,
`checkin_call_ended`, `record_alert_response` and `alert_call_ended`.
"""

import logging
import secrets
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from .models import (
    ALERT_ACKNOWLEDGED,
    ALERT_CALLING,
    ALERT_CANCELLED,
    ALERT_NO_ANSWER,
    ALERT_QUEUED,
    CALLING,
    ESC_ACKNOWLEDGED,
    ESC_CANCELLED,
    ESC_EXHAUSTED,
    ESC_IN_PROGRESS,
    ESC_NO_CONTACTS,
    MISSED,
    NEEDS_HELP,
    OK,
    PENDING,
    Alert,
    CheckIn,
    User,
    utcnow,
)
from .telephony import Telephony

log = logging.getLogger(__name__)

# A call that hasn't reported back after this long is treated as unanswered.
CALL_TIMEOUT = timedelta(minutes=5)
# A scheduled time older than this (e.g. the server was down) is skipped, not called late.
SLOT_GRACE = timedelta(hours=1)
# If the user tapped "I'm OK" in the app this recently, the scheduled call is skipped.
RECENT_APP_CHECKIN = timedelta(minutes=60)


def new_token() -> str:
    return secrets.token_urlsafe(32)


def _slot_utc(day: date, hhmm: str, tz: ZoneInfo) -> datetime:
    hh, mm = (int(part) for part in hhmm.split(":"))
    local = datetime.combine(day, time(hh, mm), tzinfo=tz)
    return local.astimezone(timezone.utc).replace(tzinfo=None)


def next_checkin_at(user: User, now: datetime | None = None) -> datetime | None:
    """The next scheduled call time (UTC) after `now`, or None if there is none."""
    if not user.active or not user.checkin_times:
        return None
    now = now or utcnow()
    tz = ZoneInfo(user.timezone)
    today = now.replace(tzinfo=timezone.utc).astimezone(tz).date()
    for offset in range(3):
        day = today + timedelta(days=offset)
        for hhmm in user.checkin_times:
            slot = _slot_utc(day, hhmm, tz)
            if slot > now:
                return slot
    return None


def local_time_text(user: User, when: datetime) -> str:
    local = when.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(user.timezone))
    return local.strftime("%H:%M on %b %d")


class CheckInService:
    def __init__(
        self,
        session_factory: sessionmaker,
        telephony: Telephony,
        base_url: str,
        require_subscription: bool = False,
    ):
        self.require_subscription = require_subscription
        self.session_factory = session_factory
        self.telephony = telephony
        self.base_url = base_url.rstrip("/")
        self.clock = utcnow  # replaced in tests

    def url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    # ------------------------------------------------------------------ scheduler

    def tick(self, now: datetime | None = None) -> None:
        now = now or self.clock()
        with self.session_factory() as s:
            self._expire_stale_calls(s, now)
            self._create_due_checkins(s, now)
            s.flush()
            self._place_due_calls(s, now)
            self._advance_escalations(s, now)
            s.commit()

    def _create_due_checkins(self, s: Session, now: datetime) -> None:
        for user in s.scalars(select(User).where(User.active.is_(True))):
            if self.require_subscription and not user.has_subscription(now):
                continue
            tz = ZoneInfo(user.timezone)
            today = now.replace(tzinfo=timezone.utc).astimezone(tz).date()
            for day in (today - timedelta(days=1), today):  # yesterday covers slots just before midnight
                for hhmm in user.checkin_times:
                    slot = _slot_utc(day, hhmm, tz)
                    if not (now - SLOT_GRACE < slot <= now):
                        continue
                    key = f"{day.isoformat()}T{hhmm}"
                    exists = s.scalar(
                        select(CheckIn.id).where(CheckIn.user_id == user.id, CheckIn.slot_key == key)
                    )
                    if exists:
                        continue
                    checkin = CheckIn(
                        user=user,
                        source="call",
                        slot_key=key,
                        scheduled_for=slot,
                        status=PENDING,
                        next_attempt_at=slot,
                    )
                    s.add(checkin)
                    recent = s.scalar(
                        select(CheckIn.id).where(
                            CheckIn.user_id == user.id,
                            CheckIn.source == "app",
                            CheckIn.status == OK,
                            CheckIn.completed_at >= slot - RECENT_APP_CHECKIN,
                        )
                    )
                    if recent:
                        checkin.status = OK
                        checkin.completed_at = now
                        checkin.next_attempt_at = None
                        checkin.note = "Skipped the call: already checked in from the app"

    def _place_due_calls(self, s: Session, now: datetime) -> None:
        due = s.scalars(
            select(CheckIn).where(CheckIn.status == PENDING, CheckIn.next_attempt_at <= now)
        ).all()
        for checkin in due:
            user = checkin.user
            if not user.active:
                checkin.status = MISSED
                checkin.note = "Check-ins were paused"
                checkin.completed_at = now
                continue
            if checkin.attempts >= user.max_attempts:
                self._mark_missed(s, checkin, now)
                continue
            checkin.attempts += 1
            checkin.status = CALLING
            checkin.call_started_at = now
            checkin.next_attempt_at = None
            try:
                checkin.call_sid = self.telephony.call(
                    user.phone,
                    self.url(f"/voice/checkin/{checkin.id}"),
                    self.url(f"/voice/checkin/{checkin.id}/status"),
                )
            except Exception:
                log.exception("Could not call user %s for check-in %s", user.id, checkin.id)
                self._no_answer(s, checkin, now)

    def _expire_stale_calls(self, s: Session, now: datetime) -> None:
        stale = s.scalars(
            select(CheckIn).where(CheckIn.status == CALLING, CheckIn.call_started_at < now - CALL_TIMEOUT)
        ).all()
        for checkin in stale:
            self._no_answer(s, checkin, now)
        stale_alerts = s.scalars(
            select(Alert).where(Alert.status == ALERT_CALLING, Alert.call_started_at < now - CALL_TIMEOUT)
        ).all()
        for alert in stale_alerts:
            alert.status = ALERT_NO_ANSWER
            alert.updated_at = now

    # ------------------------------------------------------------------ user's call

    def record_checkin_response(self, s: Session, checkin_id: int, digit: str, now: datetime | None = None) -> str:
        """Handle a key press on the user's check-in call.

        Returns "ok", "needs_help", "invalid" (ask again) or "closed" (already finished).
        """
        now = now or self.clock()
        checkin = s.get(CheckIn, checkin_id)
        if checkin is None or checkin.status not in (CALLING, PENDING):
            return "closed"
        if digit == "1":
            self._complete(checkin, OK, now, note="Answered the call: OK")
            self._cancel_open_escalations(s, checkin.user, now)
            return "ok"
        if digit == "2":
            self._complete(checkin, NEEDS_HELP, now, note="Answered the call: needs help")
            self._start_escalation(s, checkin, now)
            return "needs_help"
        return "invalid"

    def checkin_call_ended(self, s: Session, checkin_id: int, call_status: str, now: datetime | None = None) -> None:
        """Twilio says the call is over. If no key was pressed, it counts as no answer."""
        now = now or self.clock()
        checkin = s.get(CheckIn, checkin_id)
        if checkin is None or checkin.status != CALLING:
            return
        log.info("Check-in %s call ended without an answer (%s)", checkin_id, call_status)
        self._no_answer(s, checkin, now)

    def _no_answer(self, s: Session, checkin: CheckIn, now: datetime) -> None:
        if checkin.attempts >= checkin.user.max_attempts:
            self._mark_missed(s, checkin, now)
        else:
            checkin.status = PENDING
            checkin.next_attempt_at = now + timedelta(minutes=checkin.user.retry_minutes)

    def _mark_missed(self, s: Session, checkin: CheckIn, now: datetime) -> None:
        self._complete(checkin, MISSED, now, note=f"No answer after {checkin.attempts} call(s)")
        self._start_escalation(s, checkin, now)

    @staticmethod
    def _complete(checkin: CheckIn, status: str, now: datetime, note: str | None = None) -> None:
        checkin.status = status
        checkin.completed_at = now
        checkin.next_attempt_at = None
        if note:
            checkin.note = note
        checkin.user.last_status = status
        checkin.user.last_status_at = now

    # ------------------------------------------------------------------ the app

    def record_app_checkin(self, s: Session, user: User, status: str, note: str | None, now: datetime | None = None) -> CheckIn:
        """The user tapped "I'm OK" or "I need help" in the app."""
        now = now or self.clock()
        checkin = CheckIn(user=user, source="app", scheduled_for=now, status=PENDING)
        s.add(checkin)
        s.flush()
        self._complete(checkin, status, now, note=note or ("Checked in from the app" if status == OK else "Asked for help from the app"))
        if status == OK:
            # Close any call-based check-in still waiting for an answer.
            open_checkins = s.scalars(
                select(CheckIn).where(CheckIn.user_id == user.id, CheckIn.status.in_([PENDING, CALLING]))
            ).all()
            for other in open_checkins:
                self._complete(other, OK, now, note="Checked in from the app instead")
            self._cancel_open_escalations(s, user, now)
        else:
            self._start_escalation(s, checkin, now)
        return checkin

    # ------------------------------------------------------------------ alerting contacts

    def _start_escalation(self, s: Session, checkin: CheckIn, now: datetime) -> None:
        user = checkin.user
        contacts = sorted(user.contacts, key=lambda c: (c.priority, c.id))
        if not contacts:
            checkin.escalation_status = ESC_NO_CONTACTS
            log.warning("User %s needs attention but has no contacts", user.id)
            return
        checkin.escalation_status = ESC_IN_PROGRESS
        text = self.alert_sms_text(checkin)
        for position, contact in enumerate(contacts):
            alert = Alert(
                checkin=checkin,
                contact_id=contact.id,
                contact_name=contact.name,
                contact_phone=contact.phone,
                position=position,
                call=contact.notify_call,
                status=ALERT_QUEUED if contact.notify_call else ALERT_NO_ANSWER,
                updated_at=now,
            )
            s.add(alert)
            if contact.notify_sms:
                alert.sms_sent = self._safe_sms(contact.phone, text)
        s.flush()
        self._advance_one(s, checkin, now)

    def _advance_escalations(self, s: Session, now: datetime) -> None:
        for checkin in s.scalars(select(CheckIn).where(CheckIn.escalation_status == ESC_IN_PROGRESS)).all():
            self._advance_one(s, checkin, now)

    def _advance_one(self, s: Session, checkin: CheckIn, now: datetime) -> None:
        """Call the next contact unless someone acknowledged or a call is still ringing."""
        alerts = checkin.alerts
        if any(a.status == ALERT_ACKNOWLEDGED for a in alerts):
            checkin.escalation_status = ESC_ACKNOWLEDGED
            return
        if any(a.status == ALERT_CALLING for a in alerts):
            return
        for alert in alerts:
            if alert.status != ALERT_QUEUED:
                continue
            alert.status = ALERT_CALLING
            alert.call_started_at = now
            alert.updated_at = now
            try:
                alert.call_sid = self.telephony.call(
                    alert.contact_phone,
                    self.url(f"/voice/alert/{alert.id}"),
                    self.url(f"/voice/alert/{alert.id}/status"),
                )
                return
            except Exception:
                log.exception("Could not call contact for alert %s", alert.id)
                alert.status = ALERT_NO_ANSWER
        checkin.escalation_status = ESC_EXHAUSTED
        log.warning("Check-in %s: no contact acknowledged the alert", checkin.id)

    def record_alert_response(self, s: Session, alert_id: int, digit: str, now: datetime | None = None) -> str:
        """A contact pressed a key. Returns "acknowledged", "invalid" or "closed"."""
        now = now or self.clock()
        alert = s.get(Alert, alert_id)
        if alert is None or alert.status not in (ALERT_CALLING, ALERT_NO_ANSWER, ALERT_QUEUED):
            return "closed"
        if digit != "1":
            return "invalid"
        alert.status = ALERT_ACKNOWLEDGED
        alert.updated_at = now
        checkin = alert.checkin
        if checkin.escalation_status in (ESC_IN_PROGRESS, ESC_EXHAUSTED):
            checkin.escalation_status = ESC_ACKNOWLEDGED
            for other in checkin.alerts:
                if other.id == alert.id:
                    continue
                if other.status == ALERT_QUEUED:
                    other.status = ALERT_CANCELLED
                if other.sms_sent:
                    self._safe_sms(
                        other.contact_phone,
                        f"Update: {alert.contact_name} is checking on {checkin.user.name}.",
                    )
        return "acknowledged"

    def alert_call_ended(self, s: Session, alert_id: int, call_status: str, now: datetime | None = None) -> None:
        now = now or self.clock()
        alert = s.get(Alert, alert_id)
        if alert is None or alert.status != ALERT_CALLING:
            return
        alert.status = ALERT_NO_ANSWER
        alert.updated_at = now
        if alert.checkin.escalation_status == ESC_IN_PROGRESS:
            self._advance_one(s, alert.checkin, now)

    def _cancel_open_escalations(self, s: Session, user: User, now: datetime) -> None:
        """The user is OK after all: stop calling contacts and tell them."""
        open_escalations = s.scalars(
            select(CheckIn).where(
                CheckIn.user_id == user.id,
                CheckIn.escalation_status.in_([ESC_IN_PROGRESS, ESC_EXHAUSTED]),
            )
        ).all()
        for checkin in open_escalations:
            checkin.escalation_status = ESC_CANCELLED
            for alert in checkin.alerts:
                if alert.status in (ALERT_QUEUED, ALERT_CALLING):
                    alert.status = ALERT_CANCELLED
                    alert.updated_at = now
                if alert.sms_sent:
                    self._safe_sms(alert.contact_phone, f"Update: {user.name} has now checked in and is OK.")

    def alert_reason(self, checkin: CheckIn) -> str:
        if checkin.status == NEEDS_HELP:
            return "asked for help"
        return f"did not answer {checkin.attempts} check-in call{'s' if checkin.attempts != 1 else ''}"

    def alert_sms_text(self, checkin: CheckIn) -> str:
        user = checkin.user
        when = local_time_text(user, checkin.completed_at or self.clock())
        return (
            f"Check-in alert: {user.name} {self.alert_reason(checkin)} at {when} ({user.phone}). "
            "Please check on them. You may also get a call from this number."
        )

    def _safe_sms(self, to: str, body: str) -> bool:
        try:
            self.telephony.sms(to, body)
            return True
        except Exception:
            log.exception("Could not send SMS to a contact")
            return False
