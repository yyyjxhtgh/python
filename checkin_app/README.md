# Daily Check-in Call App

An automated phone call checks on a person (for example an older relative living alone)
at the times they choose. If they need help or don't answer, the app alerts their
family, caregiver or clinic.

## How it works

```
 Scheduled time (e.g. 09:00 in the user's time zone)
        │
        ▼
 Server phones the user ──► "Press 1 if you are okay, 2 if you need help"
        │
        ├─ presses 1 ─────────► status = OK  ✔
        ├─ presses 2 ─────────► status = NEEDS HELP ─┐
        └─ no answer / busy ──► retry every N minutes │
                 │ (after max tries)                  │
                 ▼                                    ▼
           status = MISSED ───────────────► ALERT CONTACTS
                                            1. every contact gets a text message
                                            2. contacts are phoned in priority order
                                               until one presses 1 ("I'll check on them")
                                            3. the others get an "X is handling it" text
```

In the mobile app the user can also:
- tap **I'm OK** to check in early. A call due within the next hour is skipped, and
  any alert already in progress is stopped, with contacts told the user is OK.
- tap **I need help** to alert contacts straight away.
- manage contacts (family, friend, caregiver, doctor, hospital, neighbour…), call times,
  number of retries, and pause calls.

## Project layout

| Folder | What it is |
|--------|------------|
| `backend/` | Python (FastAPI) server. It stores users and contacts, runs the schedule, and places calls and texts through **Twilio**. |
| `mobile/`  | Expo / React Native app for iPhone and Android. |

The server places the calls, not the phone. A phone app can't reliably make automated
calls at a set time, or call other people for the user, so a server with a telephony
service does it.

## Run the backend

```bash
cd checkin_app/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest            # 13 tests covering the whole call/alert flow
cp .env.example .env        # optional: fill in Twilio details
set -a; source .env; set +a
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

Without Twilio settings, calls and texts are **only logged** to the console, so you can
try everything for free.

### Make real calls (Twilio)

1. Create a Twilio account and buy a phone number that can make voice calls and send SMS.
2. Put `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` and `TWILIO_FROM_NUMBER` in `.env`.
3. Twilio must reach your server over HTTPS. Set `PUBLIC_BASE_URL` to its public
   address. On your own computer you can use `ngrok http 8000` and paste the https URL.
4. Requests from Twilio are checked with Twilio's signature, so keep
   `VALIDATE_TWILIO_SIGNATURE=true`.

Trial accounts can only call numbers you have verified in Twilio.

## Run the mobile app

```bash
cd checkin_app/mobile
npm install
npx expo install --fix      # aligns package versions with your Expo SDK
cp .env.example .env        # set EXPO_PUBLIC_API_URL to the backend address
npx expo start
```

Scan the QR code with the **Expo Go** app on your phone. On a real phone, `localhost`
won't work: use your computer's LAN IP (e.g. `http://192.168.1.10:8000`) or the public
URL. To publish to the App Store and Google Play, use `eas build`.

## API summary

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/users` | Register. Returns an `api_token`, sent after that as `Authorization: Bearer <token>` |
| GET / PATCH / DELETE | `/me` | View or change the schedule, pause calls, delete the account |
| GET / POST | `/me/contacts` | List or add contacts |
| PATCH / DELETE | `/me/contacts/{id}` | Edit or remove a contact |
| GET | `/me/checkins` | History, including who was alerted and what happened |
| POST | `/me/checkins` | `{"status": "ok"}` or `{"status": "needs_help"}` from the app |
| POST | `/voice/...` | Twilio webhooks (call scripts and call results) |

## Important: safety and before going live

- **This is not an emergency service.** Don't put 911 / 112 / 120 or another emergency
  number in as a contact. Automated calls to emergency lines are not allowed in many
  countries, and a recorded message can't answer a dispatcher's questions. For a
  hospital or clinic, use a number that has agreed to receive these alerts. The call
  script tells the user to dial emergency services themselves if it's life-threatening.
- **Verify phone numbers.** Registration doesn't confirm the person owns the number.
  Add an SMS code check (for example Twilio Verify) before real use, and get consent
  from contacts before alerting them.
- **Privacy.** Health and status data is personal. Use HTTPS, keep the database
  backed up and protected, and check the local rules where you operate (e.g.
  HIPAA in the US, GDPR in the EU).
- **Scale.** SQLite and the built-in scheduler are fine for one server and a few
  hundred users. For more, use PostgreSQL (`DATABASE_URL`) and run only one copy of
  the scheduler (`RUN_SCHEDULER=false` on the others).
- **Ideas for later:** an SMS reply check-in ("reply OK"), push notifications to
  family, a family view of the user's status, more call languages
  (`LANG` in `backend/app/voice.py`), and a reminder text when calls keep being missed.
