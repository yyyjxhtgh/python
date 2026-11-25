"""In-app purchases through RevenueCat.

The phone app buys a subscription from the App Store or Google Play with the
RevenueCat SDK, using the user's `billing_id` as the RevenueCat customer id.
This server learns about it in two ways:

* RevenueCat's webhook (POST /billing/revenuecat): purchases, renewals,
  cancellations, refunds and expirations, sent automatically.
* POST /me/subscription/sync, which the app calls right after a purchase so
  access starts at once instead of waiting for the webhook.

When a secret API key is configured, both ask RevenueCat's REST API for the
customer's current entitlement, so the server never trusts what the phone says.
"""

import hmac
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from .deps import get_session
from .models import User

log = logging.getLogger(__name__)

LIFETIME = datetime(9999, 1, 1)  # entitlement with no end date (e.g. a lifetime purchase)


@dataclass
class Entitlement:
    expires_at: datetime | None  # None means the customer doesn't have it
    product: str | None = None
    will_renew: bool = False


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).replace(tzinfo=None)


def _from_ms(ms: int | None) -> datetime | None:
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).replace(tzinfo=None)


class RevenueCatClient:
    """Reads a customer's entitlement from RevenueCat's REST API."""

    def __init__(self, api_key: str, entitlement: str):
        self.api_key = api_key
        self.entitlement = entitlement

    def fetch(self, app_user_id: str) -> Entitlement:
        r = httpx.get(
            f"https://api.revenuecat.com/v1/subscribers/{app_user_id}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10,
        )
        r.raise_for_status()
        subscriber = r.json()["subscriber"]
        ent = subscriber.get("entitlements", {}).get(self.entitlement)
        if not ent:
            return Entitlement(expires_at=None)
        product = ent.get("product_identifier")
        expires = _parse_time(ent.get("expires_date")) or LIFETIME
        sub = subscriber.get("subscriptions", {}).get(product, {})
        will_renew = expires != LIFETIME and not sub.get("unsubscribe_detected_at") and not sub.get("refunded_at")
        return Entitlement(expires_at=expires, product=product, will_renew=bool(will_renew))


def apply_entitlement(user: User, ent: Entitlement) -> None:
    user.subscription_expires_at = ent.expires_at
    user.subscription_product = ent.product
    user.subscription_will_renew = ent.will_renew


# Events whose expiration_at_ms gives the new end of access.
_EXTENDING = {
    "INITIAL_PURCHASE",
    "RENEWAL",
    "UNCANCELLATION",
    "PRODUCT_CHANGE",
    "NON_RENEWING_PURCHASE",
    "SUBSCRIPTION_EXTENDED",
    "TEMPORARY_ENTITLEMENT_GRANT",
}


def _entitlement_from_event(event: dict, user: User) -> Entitlement | None:
    """Fallback when no API key is set: work out access from the event alone."""
    kind = event.get("type")
    expires = _from_ms(event.get("expiration_at_ms"))
    product = event.get("product_id") or user.subscription_product
    if kind in _EXTENDING:
        return Entitlement(expires_at=expires or LIFETIME, product=product, will_renew=kind != "NON_RENEWING_PURCHASE")
    if kind == "CANCELLATION":
        # Turned off auto-renew (or refunded): access lasts until the period ends.
        return Entitlement(expires_at=expires or user.subscription_expires_at, product=product, will_renew=False)
    if kind == "EXPIRATION":
        return Entitlement(expires_at=expires, product=product, will_renew=False)
    return None  # BILLING_ISSUE, TEST, etc.: no change


def make_router(settings, client: RevenueCatClient | None) -> APIRouter:
    router = APIRouter(tags=["billing"])

    def find_user(s: Session, ids: list[str]) -> User | None:
        ids = [i for i in ids if i]
        if not ids:
            return None
        return s.scalar(select(User).where(User.billing_id.in_(ids)))

    @router.post("/billing/revenuecat", include_in_schema=False)
    async def revenuecat_webhook(request: Request, s: Session = Depends(get_session)):
        expected = settings.revenuecat_webhook_auth
        given = request.headers.get("Authorization", "")
        if not expected or not hmac.compare_digest(given, expected):
            raise HTTPException(status_code=401, detail="Bad webhook authorization")
        event = (await request.json()).get("event", {})
        kind = event.get("type")

        ids = [event.get("app_user_id"), event.get("original_app_user_id"), *(event.get("aliases") or [])]
        if kind == "TRANSFER":  # purchases moved between customers (e.g. "restore" on another account)
            ids = [*(event.get("transferred_from") or []), *(event.get("transferred_to") or [])]
            users = s.scalars(select(User).where(User.billing_id.in_([i for i in ids if i]))).all()
        else:
            user = find_user(s, ids)
            users = [user] if user else []
        if not users:
            log.info("RevenueCat %s event for an unknown customer", kind)
            return {"ok": True}

        entitlements = event.get("entitlement_ids")
        if kind != "TRANSFER" and entitlements and settings.revenuecat_entitlement not in entitlements:
            return {"ok": True}  # about some other product

        for user in users:
            if client:
                ent = client.fetch(user.billing_id)
            else:
                ent = _entitlement_from_event(event, user) if kind != "TRANSFER" else None
            if ent:
                apply_entitlement(user, ent)
                log.info("User %s subscription now ends %s (%s)", user.id, ent.expires_at, kind)
        s.commit()
        return {"ok": True}

    return router
