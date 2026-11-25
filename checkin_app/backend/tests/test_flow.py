from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.db import make_session_factory
from app.main import create_app
from app.models import CheckIn
from app.telephony import ConsoleTelephony

BASE = "https://checkin.example.com"


@pytest.fixture
def env():
    settings = Settings(database_url="sqlite://", public_base_url=BASE, run_scheduler=False)
    tel = ConsoleTelephony()
    factory = make_session_factory("sqlite://")
    app = create_app(settings, tel, factory)
    client = TestClient(app)
    service = app.state.service
    # Tests set the time explicitly: tick(now) also moves this clock forward.
    service.clock = lambda: service.now
    service.now = NINE_AM
    real_tick = service.tick

    def tick(now):
        service.now = now
        real_tick(now)

    service.tick = tick
    return client, tel, service, factory


def register(client, **overrides):
    body = {
        "name": "Grandma Li",
        "phone": "+1 415 555 0100",
        "timezone": "America/New_York",
        "checkin_times": ["09:00"],
        "max_attempts": 2,
        "retry_minutes": 10,
    } | overrides
    r = client.post("/users", json=body)
    assert r.status_code == 201, r.text
    data = r.json()
    headers = {"Authorization": f"Bearer {data['api_token']}"}
    return data["user"], headers


def add_contacts(client, headers):
    for name, phone, rel, prio in [
        ("Daughter", "+14155550111", "family", 1),
        ("City Clinic", "+14155550122", "hospital", 2),
    ]:
        r = client.post(
            "/me/contacts", json={"name": name, "phone": phone, "relation": rel, "priority": prio}, headers=headers
        )
        assert r.status_code == 201, r.text


# 09:00 in New York on 2026-11-25 is 14:00 UTC.
NINE_AM = datetime(2026, 11, 25, 14, 0)


def latest_checkin(factory):
    with factory() as s:
        return s.query(CheckIn).order_by(CheckIn.id.desc()).first()


def test_register_validates_and_rejects_duplicates(env):
    client, *_ = env
    user, headers = register(client)
    assert user["phone"] == "+14155550100"
    assert client.post("/users", json={"name": "X", "phone": "+14155550100"}).status_code == 409
    assert client.post("/users", json={"name": "X", "phone": "12345"}).status_code == 422
    assert client.post("/users", json={"name": "X", "phone": "+14155550199", "timezone": "Mars/Base"}).status_code == 422
    assert client.post("/users", json={"name": "X", "phone": "+14155550199", "checkin_times": ["25:00"]}).status_code == 422
    assert client.get("/me").status_code == 401
    assert client.get("/me", headers=headers).json()["name"] == "Grandma Li"


def test_user_answers_ok(env):
    client, tel, service, factory = env
    _, headers = register(client)

    service.tick(NINE_AM - timedelta(minutes=1))
    assert tel.calls == []

    service.tick(NINE_AM + timedelta(seconds=20))
    assert len(tel.calls) == 1
    assert tel.calls[0]["to"] == "+14155550100"
    checkin = latest_checkin(factory)

    script = client.post(f"/voice/checkin/{checkin.id}")
    assert "press 1" in script.text and "<Gather" in script.text

    r = client.post(f"/voice/checkin/{checkin.id}/response", data={"Digits": "1"})
    assert "okay" in r.text
    client.post(f"/voice/checkin/{checkin.id}/status", data={"CallStatus": "completed"})

    me = client.get("/me", headers=headers).json()
    assert me["last_status"] == "ok"
    history = client.get("/me/checkins", headers=headers).json()
    assert history[0]["status"] == "ok" and history[0]["escalation_status"] is None

    # Ticking again the same morning does not call twice.
    service.tick(NINE_AM + timedelta(minutes=5))
    assert len(tel.calls) == 1


def test_no_answer_retries_then_alerts_contacts_in_order(env):
    client, tel, service, factory = env
    _, headers = register(client)
    add_contacts(client, headers)

    service.tick(NINE_AM)
    checkin = latest_checkin(factory)
    client.post(f"/voice/checkin/{checkin.id}/status", data={"CallStatus": "no-answer"})
    assert latest_checkin(factory).status == "pending"

    service.tick(NINE_AM + timedelta(minutes=5))  # too early for the retry
    assert len(tel.calls) == 1
    service.tick(NINE_AM + timedelta(minutes=10))
    assert len(tel.calls) == 2
    client.post(f"/voice/checkin/{checkin.id}/status", data={"CallStatus": "busy"})

    # Out of attempts: both contacts get a text, the first one gets a call.
    checkin = latest_checkin(factory)
    assert checkin.status == "missed"
    assert checkin.escalation_status == "in_progress"
    assert {m["to"] for m in tel.messages} == {"+14155550111", "+14155550122"}
    assert "did not answer 2 check-in calls" in tel.messages[0]["body"]
    assert tel.calls[-1]["to"] == "+14155550111"

    # The daughter doesn't pick up, so the clinic is called next.
    alerts = client.get("/me/checkins", headers=headers).json()[0]["alerts"]
    assert [a["status"] for a in alerts] == ["calling", "queued"]
    first_alert_url = tel.calls[-1]["status_callback"].removeprefix(BASE)
    client.post(first_alert_url, data={"CallStatus": "no-answer"})
    assert tel.calls[-1]["to"] == "+14155550122"

    # The clinic presses 1.
    second_alert = tel.calls[-1]["url"].removeprefix(BASE)
    assert "check-in alert for Grandma Li" in client.post(second_alert).text
    r = client.post(f"{second_alert}/response", data={"Digits": "1"})
    assert "handling this" in r.text
    assert latest_checkin(factory).escalation_status == "acknowledged"
    assert any("City Clinic is checking on Grandma Li" in m["body"] for m in tel.messages)

    service.tick(NINE_AM + timedelta(minutes=30))
    assert len(tel.calls) == 4  # nobody else is called


def test_pressing_2_asks_for_help(env):
    client, tel, service, factory = env
    _, headers = register(client)
    add_contacts(client, headers)
    service.tick(NINE_AM)
    checkin = latest_checkin(factory)
    r = client.post(f"/voice/checkin/{checkin.id}/response", data={"Digits": "2"})
    assert "contacting your emergency contacts" in r.text
    assert client.get("/me", headers=headers).json()["last_status"] == "needs_help"
    assert "asked for help" in tel.messages[0]["body"]
    assert tel.calls[-1]["to"] == "+14155550111"


def test_wrong_key_repeats_the_question(env):
    client, _, service, factory = env
    register(client)
    service.tick(NINE_AM)
    checkin = latest_checkin(factory)
    r = client.post(f"/voice/checkin/{checkin.id}/response", data={"Digits": "7"})
    assert "<Redirect>" in r.text
    assert latest_checkin(factory).status == "calling"


def test_lost_callback_counts_as_no_answer(env):
    client, tel, service, factory = env
    register(client, max_attempts=1)
    service.tick(NINE_AM)
    service.tick(NINE_AM + timedelta(minutes=6))
    checkin = latest_checkin(factory)
    assert checkin.status == "missed"
    assert checkin.escalation_status == "no_contacts"


def test_app_ok_skips_call_and_cancels_escalation(env):
    client, tel, service, factory = env
    _, headers = register(client, max_attempts=1)
    add_contacts(client, headers)

    # Missed check-in starts an escalation...
    service.tick(NINE_AM)
    checkin = latest_checkin(factory)
    client.post(f"/voice/checkin/{checkin.id}/status", data={"CallStatus": "no-answer"})
    assert latest_checkin(factory).escalation_status == "in_progress"

    # ...then the user taps "I'm OK" in the app.
    r = client.post("/me/checkins", json={"status": "ok"}, headers=headers)
    assert r.status_code == 201
    with factory() as s:
        assert s.get(CheckIn, checkin.id).escalation_status == "cancelled"
    assert any("has now checked in and is OK" in m["body"] for m in tel.messages)
    calls_before = len(tel.calls)
    service.tick(NINE_AM + timedelta(minutes=20))
    assert len(tel.calls) == calls_before


def test_recent_app_checkin_skips_the_scheduled_call(env):
    client, tel, service, factory = env
    _, headers = register(client)
    with factory() as s:
        from app.models import User

        user = s.query(User).one()
        service.record_app_checkin(s, user, "ok", None, now=NINE_AM - timedelta(minutes=30))
        s.commit()
    service.tick(NINE_AM)
    assert tel.calls == []
    assert latest_checkin(factory).note.startswith("Skipped the call")


def test_app_help_button_alerts_contacts(env):
    client, tel, _, _ = env
    _, headers = register(client)
    add_contacts(client, headers)
    r = client.post("/me/checkins", json={"status": "needs_help", "note": "I fell"}, headers=headers)
    assert r.json()["escalation_status"] == "in_progress"
    assert len(tel.messages) == 2
    assert tel.calls[-1]["to"] == "+14155550111"


def test_paused_user_is_not_called(env):
    client, tel, service, _ = env
    _, headers = register(client)
    client.patch("/me", json={"active": False}, headers=headers)
    service.tick(NINE_AM)
    assert tel.calls == []


def test_multiple_times_and_next_checkin(env):
    client, tel, service, _ = env
    _, headers = register(client, checkin_times=["20:00", "09:00"])
    me = client.get("/me", headers=headers).json()
    assert me["checkin_times"] == ["09:00", "20:00"]
    service.tick(NINE_AM)
    service.tick(NINE_AM + timedelta(hours=11))  # 20:00 New York
    assert len(tel.calls) == 2


def test_contacts_are_private(env):
    client, *_ = env
    _, a = register(client)
    _, b = register(client, phone="+14155550199", name="Other")
    add_contacts(client, a)
    contact_id = client.get("/me/contacts", headers=a).json()[0]["id"]
    assert client.delete(f"/me/contacts/{contact_id}", headers=b).status_code == 404
    assert client.get("/me/contacts", headers=b).json() == []


def test_twilio_signature_is_checked_when_configured():
    settings = Settings(
        database_url="sqlite://", public_base_url=BASE, run_scheduler=False, twilio_auth_token="secret"
    )
    client = TestClient(create_app(settings, ConsoleTelephony(), make_session_factory("sqlite://")))
    assert client.post("/voice/checkin/1/status", data={"CallStatus": "completed"}).status_code == 403

    from twilio.request_validator import RequestValidator

    params = {"CallStatus": "completed"}
    sig = RequestValidator("secret").compute_signature(f"{BASE}/voice/checkin/1/status", params)
    r = client.post("/voice/checkin/1/status", data=params, headers={"X-Twilio-Signature": sig})
    assert r.status_code == 204
