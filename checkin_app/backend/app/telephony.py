"""Placing phone calls and sending SMS.

`TwilioTelephony` does it for real. `ConsoleTelephony` only logs and records
what it would have done, for local development and tests.
"""

import itertools
import logging
from dataclasses import dataclass, field
from typing import Protocol

log = logging.getLogger(__name__)


class Telephony(Protocol):
    def call(self, to: str, twiml_url: str, status_callback_url: str) -> str:
        """Start a call that plays the script at `twiml_url`. Returns the call id."""

    def sms(self, to: str, body: str) -> str:
        """Send a text message. Returns the message id."""


class TwilioTelephony:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        from twilio.rest import Client

        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def call(self, to: str, twiml_url: str, status_callback_url: str) -> str:
        call = self.client.calls.create(
            to=to,
            from_=self.from_number,
            url=twiml_url,
            status_callback=status_callback_url,
            status_callback_event=["completed"],
            timeout=30,  # seconds to ring before giving up
        )
        return call.sid

    def sms(self, to: str, body: str) -> str:
        message = self.client.messages.create(to=to, from_=self.from_number, body=body)
        return message.sid


@dataclass
class ConsoleTelephony:
    calls: list[dict] = field(default_factory=list)
    messages: list[dict] = field(default_factory=list)
    _ids: itertools.count = field(default_factory=lambda: itertools.count(1))

    def call(self, to: str, twiml_url: str, status_callback_url: str) -> str:
        sid = f"CA-fake-{next(self._ids)}"
        self.calls.append({"sid": sid, "to": to, "url": twiml_url, "status_callback": status_callback_url})
        log.info("[fake call] %s -> %s (script %s)", sid, to, twiml_url)
        return sid

    def sms(self, to: str, body: str) -> str:
        sid = f"SM-fake-{next(self._ids)}"
        self.messages.append({"sid": sid, "to": to, "body": body})
        log.info("[fake sms] %s -> %s: %s", sid, to, body)
        return sid
