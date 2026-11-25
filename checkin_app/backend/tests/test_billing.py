from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.billing import LIFETIME, Entitlement
from app.config import Settings
from app.db import make_session_factory
from app.main import create_app
from app.models import User
from app.telephony import ConsoleTelephony

WEBHOOK_AUTH = "Bearer webhook-secret"


class FakeRevenueCat:
    """Stands in for RevenueCat's REST API."""

    def __init__(self):
        self.entitlements: dict[str, Entitlement] = {}
        self.fail = False

    def fetch(self, app_user_id: str) -> Entitlement:
        if self.fail:
            raise RuntimeError("RevenueCat is down")
        return self.entitlements.get(app_user_id, Entitlement(expires_at=None))


def make(require=True, with_api=True):
    settings = Settings(
        database_url="sqlite://",
        run_scheduler=False,
        require_subscription=require,
        revenuecat_webhook_auth=WEBHOOK_AUTH,
    )
    tel = ConsoleTelephony()
    factory = make_session_factory("sqlite://")
    rc = FakeRevenueCat() if with_api else None
    app = create_app(settings, tel, factory, revenuecat=rc)
    client = TestClient(app)
    r = client.post("/users", json={"name": "Mom", "phone": "+14155550100", "timezone": "UTC", "checkin_times": ["09:00"]})
    data = r.json()
    headers = {"Authorization": f"Bearer {data['api_token']}"}
    return client, tel, app.state.service, factory, rc, data["user"], headers


def ms(dt: datetime) -> int:
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)


def future(days=30) -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0) + timedelta(days=days)


def nine_am_today():
    return datetime.now(timezone.utc).replace(tzinfo=None, hour=9, minute=0, second=0, microsecond=0)


def test_no_subscription_means_no_scheduled_calls():
    client, tel, service, *_, user, headers = make()
    assert user["subscription_required"] is True
    assert user["subscription_active"] is False
    assert user["calls_enabled"] is False
    service.tick(nine_am_today())
    assert tel.calls == []


def test_help_button_works_without_a_subscription():
    client, tel, *_, headers = make()
    client.post("/me/contacts", json={"name": "Son", "phone": "+14155550111"}, headers=headers)
    r = client.post("/me/checkins", json={"status": "needs_help"}, headers=headers)
    assert r.status_code == 201
    assert len(tel.messages) == 1  # safety feature is never behind the paywall


def test_sync_after_purchase_turns_calls_on():
    client, tel, service, factory, rc, user, headers = make()
    rc.entitlements[user["billing_id"]] = Entitlement(expires_at=future(), product="checkin_monthly", will_renew=True)
    me = client.post("/me/subscription/sync", headers=headers).json()
    assert me["subscription_active"] is True
    assert me["calls_enabled"] is True
    assert me["subscription_will_renew"] is True
    service.tick(nine_am_today())
    assert len(tel.calls) == 1


def test_sync_reports_revenuecat_errors():
    client, *_, rc, user, headers = make()
    rc.fail = True
    assert client.post("/me/subscription/sync", headers=headers).status_code == 502


def test_webhook_requires_the_shared_secret():
    client, *_, user, headers = make()
    body = {"event": {"type": "INITIAL_PURCHASE", "app_user_id": user["billing_id"]}}
    assert client.post("/billing/revenuecat", json=body).status_code == 401
    assert client.post("/billing/revenuecat", json=body, headers={"Authorization": "wrong"}).status_code == 401


def test_webhook_uses_revenuecat_api_as_the_truth():
    client, *_, rc, user, headers = make()
    rc.entitlements[user["billing_id"]] = Entitlement(expires_at=future(365), product="checkin_yearly", will_renew=True)
    # Even if the event itself says something else, the API answer wins.
    body = {"event": {"type": "RENEWAL", "app_user_id": user["billing_id"], "expiration_at_ms": ms(future(1))}}
    assert client.post("/billing/revenuecat", json=body, headers={"Authorization": WEBHOOK_AUTH}).status_code == 200
    me = client.get("/me", headers=headers).json()
    assert me["subscription_active"] is True
    assert me["subscription_expires_at"].startswith(future(365).date().isoformat())


@pytest.mark.parametrize(
    "events, active, renews",
    [
        ([("INITIAL_PURCHASE", 30)], True, True),
        ([("INITIAL_PURCHASE", 30), ("CANCELLATION", 30)], True, False),  # still paid up until the end
        ([("INITIAL_PURCHASE", 30), ("EXPIRATION", -1)], False, False),
        ([("NON_RENEWING_PURCHASE", None)], True, False),  # e.g. lifetime
    ],
)
def test_webhook_events_without_api_key(events, active, renews):
    client, *_, user, headers = make(with_api=False)
    for kind, days in events:
        event = {"type": kind, "app_user_id": user["billing_id"], "product_id": "checkin_monthly", "entitlement_ids": ["premium"]}
        if days is not None:
            event["expiration_at_ms"] = ms(future(days))
        client.post("/billing/revenuecat", json={"event": event}, headers={"Authorization": WEBHOOK_AUTH})
    me = client.get("/me", headers=headers).json()
    assert me["subscription_active"] is active
    assert me["subscription_will_renew"] is renews


def test_webhook_ignores_other_entitlements_and_unknown_customers():
    client, *_, user, headers = make(with_api=False)
    auth = {"Authorization": WEBHOOK_AUTH}
    other = {"type": "INITIAL_PURCHASE", "app_user_id": user["billing_id"], "entitlement_ids": ["something_else"],
             "expiration_at_ms": ms(future())}
    unknown = {"type": "INITIAL_PURCHASE", "app_user_id": "nobody", "expiration_at_ms": ms(future())}
    assert client.post("/billing/revenuecat", json={"event": other}, headers=auth).status_code == 200
    assert client.post("/billing/revenuecat", json={"event": unknown}, headers=auth).status_code == 200
    assert client.get("/me", headers=headers).json()["subscription_active"] is False


def test_billing_id_is_random_not_the_user_id():
    *_, factory, rc, user, headers = make()
    assert user["billing_id"] != str(user["id"])
    assert len(user["billing_id"]) >= 32


def test_subscription_not_required_by_default():
    client, tel, service, *_, user, headers = make(require=False)
    assert user["calls_enabled"] is True
    service.tick(nine_am_today())
    assert len(tel.calls) == 1


def test_lifetime_entitlement():
    client, *_, rc, user, headers = make()
    rc.entitlements[user["billing_id"]] = Entitlement(expires_at=LIFETIME, product="checkin_lifetime")
    me = client.post("/me/subscription/sync", headers=headers).json()
    assert me["subscription_active"] is True


def test_revenuecat_client_parses_api_response(monkeypatch):
    import httpx

    from app.billing import RevenueCatClient

    payload = {
        "subscriber": {
            "entitlements": {
                "premium": {"expires_date": "2030-01-02T03:04:05Z", "product_identifier": "checkin_monthly"}
            },
            "subscriptions": {"checkin_monthly": {"unsubscribe_detected_at": "2029-12-20T00:00:00Z"}},
        }
    }
    seen = {}

    def fake_get(url, headers, timeout):
        seen["url"], seen["auth"] = url, headers["Authorization"]
        return httpx.Response(200, json=payload, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", fake_get)
    ent = RevenueCatClient("sk_test", "premium").fetch("abc123")
    assert seen == {"url": "https://api.revenuecat.com/v1/subscribers/abc123", "auth": "Bearer sk_test"}
    assert ent.expires_at == datetime(2030, 1, 2, 3, 4, 5)
    assert ent.product == "checkin_monthly"
    assert ent.will_renew is False  # user turned off auto-renew

    payload["subscriber"]["entitlements"] = {}
    assert RevenueCatClient("sk_test", "premium").fetch("abc123").expires_at is None
