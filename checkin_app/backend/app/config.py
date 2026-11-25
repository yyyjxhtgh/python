"""Settings read from environment variables (see .env.example)."""

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    database_url: str = "sqlite:///./checkin.db"
    # Public HTTPS address of this server. Twilio calls it back for call scripts.
    public_base_url: str = "http://localhost:8000"
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_from_number: str | None = None
    # Check Twilio's signature on webhook requests (turn off only for local testing).
    validate_twilio_signature: bool = True
    run_scheduler: bool = True
    scheduler_interval_seconds: int = 30
    # In-app purchases (RevenueCat). When required, scheduled calls only run for subscribers.
    require_subscription: bool = False
    revenuecat_api_key: str | None = None  # secret API key, used to confirm purchases
    revenuecat_webhook_auth: str | None = None  # the Authorization value set on the RevenueCat webhook
    revenuecat_entitlement: str = "premium"

    @property
    def twilio_enabled(self) -> bool:
        return bool(self.twilio_account_sid and self.twilio_auth_token and self.twilio_from_number)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.getenv("DATABASE_URL", cls.database_url),
            public_base_url=os.getenv("PUBLIC_BASE_URL", cls.public_base_url).rstrip("/"),
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID") or None,
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN") or None,
            twilio_from_number=os.getenv("TWILIO_FROM_NUMBER") or None,
            validate_twilio_signature=_env_bool("VALIDATE_TWILIO_SIGNATURE", True),
            run_scheduler=_env_bool("RUN_SCHEDULER", True),
            scheduler_interval_seconds=int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "30")),
            require_subscription=_env_bool("REQUIRE_SUBSCRIPTION", False),
            revenuecat_api_key=os.getenv("REVENUECAT_API_KEY") or None,
            revenuecat_webhook_auth=os.getenv("REVENUECAT_WEBHOOK_AUTH") or None,
            revenuecat_entitlement=os.getenv("REVENUECAT_ENTITLEMENT", cls.revenuecat_entitlement),
        )
