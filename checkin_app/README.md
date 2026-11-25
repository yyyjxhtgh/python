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
- subscribe in the **Plan** tab (see *In-app purchase* below).

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
python -m pytest            # 28 tests: call/alert flow and purchases
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

## In-app purchase (subscription)

Scheduled calls cost money (phone minutes and texts), so they can be sold as a
subscription bought inside the app. The **I need help** button always stays free.

```
 Phone app ──buy──► App Store / Google Play ──► RevenueCat ──webhook──► this server
     │                                                                    │
     └── after buying: POST /me/subscription/sync ── server asks RevenueCat ┘
                                                     "is this customer paid up?"
```

- The store payment is handled by **RevenueCat** (free up to $2,500/month of revenue),
  which works with both Apple and Google.
- The server never trusts the phone. It confirms every purchase with RevenueCat's API,
  and the RevenueCat webhook keeps it up to date on renewals, cancellations, refunds
  and expiry.
- Each user gets a random `billing_id` as their RevenueCat customer id, so purchases
  can't leak to another account.
- With `REQUIRE_SUBSCRIPTION=false` (the default), everything is free, which is useful
  while testing.

Apple and Google require their own payment system for subscriptions sold inside an
app. They keep 15% (small developers / after the first year) to 30% of the price.

### Setup checklist

1. **Apple** (App Store Connect, needs the $99/year developer account):
   create the app, then under *Subscriptions* create a group with products such as
   `checkin_monthly` and `checkin_yearly`. Add prices and an optional free trial.
   Accept the Paid Apps agreement and fill in banking and tax details.
2. **Google** (Play Console, $25 one-time fee): create the app and add the same
   subscription products under *Monetize → Subscriptions*. Google requires an app
   build uploaded to a testing track before products can be bought.
3. **RevenueCat** (revenuecat.com):
   - Add the iOS and Android apps. Link them with an App Store Connect API key and a
     Google Play service account.
   - Create an **entitlement** called `premium` and attach both products to it.
   - Create an **offering** (mark it *current*) with monthly and yearly packages.
     The app shows whatever this offering contains.
   - Under *Integrations → Webhooks*, add the URL `https://YOUR-SERVER/billing/revenuecat`
     and set an *Authorization header* value, for example `Bearer <long random string>`.
4. **Server `.env`:** `REQUIRE_SUBSCRIPTION=true`, `REVENUECAT_API_KEY=sk_...` (secret key),
   and `REVENUECAT_WEBHOOK_AUTH` set to the exact header value from step 3.
5. **App `mobile/.env`:** `EXPO_PUBLIC_RC_IOS_KEY`, `EXPO_PUBLIC_RC_ANDROID_KEY` (public
   SDK keys), plus your Terms of Use and Privacy Policy links. Apple rejects
   subscription apps without them.

### Testing purchases

Store purchases **don't work in Expo Go**. Make a development build instead:

```bash
cd checkin_app/mobile
npm install -g eas-cli && eas login
npm run build:dev            # builds an installable test app in the cloud
npm start                    # then open the installed dev app
```

- **iPhone:** create a *Sandbox tester* in App Store Connect (Users and Access →
  Sandbox) and sign in with it when buying. Sandbox subscriptions renew quickly
  (a month lasts about 5 minutes), so you can watch renewals and expiry.
- **Android:** add your Google account as a *license tester* in Play Console. Test
  purchases aren't charged.
- Check the result in the **Plan** tab, and in the RevenueCat dashboard under *Customers*.

If you ran an earlier version, delete `backend/checkin.db` once. The subscription
fields are new columns, and the simple SQLite setup doesn't upgrade old files.

## API summary

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/users` | Register. Returns an `api_token`, sent after that as `Authorization: Bearer <token>` |
| GET / PATCH / DELETE | `/me` | View or change the schedule, pause calls, delete the account |
| GET / POST | `/me/contacts` | List or add contacts |
| PATCH / DELETE | `/me/contacts/{id}` | Edit or remove a contact |
| GET | `/me/checkins` | History, including who was alerted and what happened |
| POST | `/me/checkins` | `{"status": "ok"}` or `{"status": "needs_help"}` from the app |
| POST | `/me/subscription/sync` | Re-check the user's purchase with RevenueCat (the app calls this after buying) |
| POST | `/voice/...` | Twilio webhooks (call scripts and call results) |
| POST | `/billing/revenuecat` | RevenueCat webhook (purchases, renewals, cancellations) |

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
