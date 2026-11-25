"""Twilio webhooks: the spoken call scripts and call results."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator
from twilio.twiml.voice_response import Gather, VoiceResponse

from .deps import get_service, get_session
from .models import Alert, CheckIn
from .service import CheckInService

LANG = "en-US"


async def verify_twilio(request: Request) -> None:
    settings = request.app.state.settings
    if not (settings.validate_twilio_signature and settings.twilio_auth_token):
        return
    form = await request.form()
    url = settings.public_base_url + request.url.path
    if request.url.query:
        url += "?" + request.url.query
    validator = RequestValidator(settings.twilio_auth_token)
    if not validator.validate(url, dict(form), request.headers.get("X-Twilio-Signature", "")):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")


router = APIRouter(prefix="/voice", dependencies=[Depends(verify_twilio)], include_in_schema=False)


def twiml(response: VoiceResponse) -> Response:
    return Response(content=str(response), media_type="application/xml")


def _hangup(message: str) -> Response:
    r = VoiceResponse()
    r.say(message, language=LANG)
    r.hangup()
    return twiml(r)


# ---------------------------------------------------------------- the user's call


@router.post("/checkin/{checkin_id}")
def checkin_script(checkin_id: int, s: Session = Depends(get_session), service: CheckInService = Depends(get_service)):
    checkin = s.get(CheckIn, checkin_id)
    if checkin is None:
        return _hangup("Sorry, something went wrong. Goodbye.")
    r = VoiceResponse()
    gather = Gather(num_digits=1, timeout=8, action=service.url(f"/voice/checkin/{checkin_id}/response"))
    prompt = (
        f"Hello {checkin.user.name}. This is your check-in call. "
        "If you are okay, press 1. If you need help, press 2."
    )
    gather.say(prompt, language=LANG)
    gather.pause(length=2)
    gather.say(prompt, language=LANG)
    r.append(gather)
    r.say("We did not hear a response. We will call again soon. Goodbye.", language=LANG)
    r.hangup()
    return twiml(r)


@router.post("/checkin/{checkin_id}/response")
def checkin_response(
    checkin_id: int,
    Digits: str = Form(""),
    s: Session = Depends(get_session),
    service: CheckInService = Depends(get_service),
):
    result = service.record_checkin_response(s, checkin_id, Digits)
    s.commit()
    if result == "ok":
        return _hangup("Thank you. We have noted that you are okay. Have a good day. Goodbye.")
    if result == "needs_help":
        return _hangup(
            "We are contacting your emergency contacts now. "
            "If this is a life threatening emergency, hang up and call your local emergency number."
        )
    if result == "invalid":
        r = VoiceResponse()
        r.say("Sorry, I did not understand.", language=LANG)
        r.redirect(service.url(f"/voice/checkin/{checkin_id}"))
        return twiml(r)
    return _hangup("This check-in is already complete. Goodbye.")


@router.post("/checkin/{checkin_id}/status")
def checkin_status(
    checkin_id: int,
    CallStatus: str = Form(""),
    s: Session = Depends(get_session),
    service: CheckInService = Depends(get_service),
):
    service.checkin_call_ended(s, checkin_id, CallStatus)
    s.commit()
    return Response(status_code=204)


# ---------------------------------------------------------------- calls to contacts


@router.post("/alert/{alert_id}")
def alert_script(alert_id: int, s: Session = Depends(get_session), service: CheckInService = Depends(get_service)):
    alert = s.get(Alert, alert_id)
    if alert is None:
        return _hangup("Sorry, something went wrong. Goodbye.")
    checkin = alert.checkin
    user = checkin.user
    r = VoiceResponse()
    gather = Gather(num_digits=1, timeout=8, action=service.url(f"/voice/alert/{alert_id}/response"))
    prompt = (
        f"Hello {alert.contact_name}. This is an automated check-in alert for {user.name}. "
        f"{user.name} {service.alert_reason(checkin)}. "
        "Please check on them. Press 1 to confirm that you will handle this."
    )
    gather.say(prompt, language=LANG)
    gather.pause(length=2)
    gather.say(prompt, language=LANG)
    r.append(gather)
    r.say("No confirmation received. We will contact the next person on the list. Goodbye.", language=LANG)
    r.hangup()
    return twiml(r)


@router.post("/alert/{alert_id}/response")
def alert_response(
    alert_id: int,
    Digits: str = Form(""),
    s: Session = Depends(get_session),
    service: CheckInService = Depends(get_service),
):
    result = service.record_alert_response(s, alert_id, Digits)
    s.commit()
    if result == "acknowledged":
        return _hangup("Thank you. We have recorded that you are handling this. Goodbye.")
    if result == "invalid":
        r = VoiceResponse()
        r.redirect(service.url(f"/voice/alert/{alert_id}"))
        return twiml(r)
    return _hangup("This alert has already been handled. Goodbye.")


@router.post("/alert/{alert_id}/status")
def alert_status(
    alert_id: int,
    CallStatus: str = Form(""),
    s: Session = Depends(get_session),
    service: CheckInService = Depends(get_service),
):
    service.alert_call_ended(s, alert_id, CallStatus)
    s.commit()
    return Response(status_code=204)
