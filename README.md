# Spike API — Python Flask Local Demo

This demo shows **exactly where and how to run** Python files to connect your local web app (localhost) to the Spike API using **HMAC authentication**.

## 1) Prerequisites
- Python 3.10+ installed
- Your **Spike Application ID** and **HMAC key** (from the Spike Admin Console)
- Windows (PowerShell) or Git Bash / macOS Terminal

## 2) Setup
```bash
# Unzip this project, then in your terminal:
cd spike_demo_flask

# Create and activate a virtual environment (Windows PowerShell)
python -m venv env
.\env\Scripts\Activate.ps1

# (On Git Bash instead: source env/Scripts/activate)
# (On macOS/Linux: source env/bin/activate)

# Install dependencies
pip install -r requirements.txt

# Configure secrets: copy .env.example to .env and fill values
copy .env.example .env   # Windows PowerShell
# or: cp .env.example .env
# then open .env and set SPIKE_APP_ID and SPIKE_HMAC_KEY
```

## 3) Run the Flask app (your local web server)
```bash
# In the same terminal (venv activated):
python app.py
# or:
# set FLASK_APP=app.py ; flask run
```
It starts on `http://127.0.0.1:5000` (unless you changed the `PORT` in `.env`).

## 4) Get a token from Spike (HMAC auth)
Send a POST request to your local endpoint which signs your user and exchanges for a token:

```bash
curl -X POST http://127.0.0.1:5000/auth ^
  -H "Content-Type: application/json" ^
  -d "{ \"userId\": \"my_local_user_123\" }"
```

Response:
```json
{ "access_token": "..." }
```

Under the hood this calls Spike's endpoint:
`POST https://app-api.spikeapi.com/v3/auth/hmac`

## 5) Use the token to call Spike endpoints (example: /userinfo)
```bash
# Replace <TOKEN> with the access_token from step 4
curl "http://127.0.0.1:5000/userinfo" -H "Authorization: Bearer <TOKEN>"
```
This proxies to Spike's `GET https://app-api.spikeapi.com/v3/userinfo` and returns the JSON.

## 6) One-off: get a token via script
```bash
python get_token.py my_local_user_123
```
The script prints the token. You can paste it into Postman or use it in requests.

## Notes
- **Never commit your `.env`** (HMAC secret) to git.
- The HMAC signature is generated with SHA-256 using your Spike HMAC key and the `application_user_id`.
- Use the returned `access_token` in `Authorization: Bearer <token>` for all subsequent API calls.
- If you see 401 or 403, double-check your `SPIKE_APP_ID`, `SPIKE_HMAC_KEY`, and the exact `userId` used when signing.
