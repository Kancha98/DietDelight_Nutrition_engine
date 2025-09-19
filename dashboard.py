from flask import Blueprint, render_template, redirect, request, url_for, session, flash
from models import get_user_by_id, seed_fake_libre
import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from models import get_conn
from models import calculate_sugar_grade
from models import get_libre_glucose, backfill_libre_glucose

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login"))

    user = get_user_by_id(uid)
    if not user:
        session.clear()
        flash("Session expired. Please sign in again.", "error")
        return redirect(url_for("auth.login"))

    has_fitbit = bool(session.get("spike_token"))
    return render_template("dashboard.html", user=user, has_fitbit=has_fitbit)


@dashboard_bp.route("/connect/fitbit")
def connect_fitbit():
    token = session.get("spike_token")
    if not token:
        flash("No Spike token, please log in again.", "error")
        return redirect(url_for("auth.login"))

    resp = requests.get(
        "https://app-api.spikeapi.com/v3/providers/fitbit/integration/init_url",
        headers={"Authorization": f"Bearer {token}"}
    )

    if resp.ok:
        redirect_url = resp.json().get("path")
        return redirect(redirect_url or url_for("dashboard.dashboard"))
    else:
        flash("Failed to start Fitbit connection", "error")
        return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/fitbit-data")
def fitbit_data():
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login"))

    token = session.get("spike_token")
    if not token:
        flash("No Spike token, please log in again.", "error")
        return redirect(url_for("auth.login"))

    try:
        url = "https://app-api.spikeapi.com/v3/queries/timeseries"
        headers = {"Authorization": f"Bearer {token}"}

        end = datetime.now(timezone.utc)
        start = end - timedelta(days=7)

        params = {
            "metric": "steps",
            "from_timestamp": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to_timestamp": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "interval": "5minute"
        }

        resp = requests.get(url, headers=headers, params=params)
        if resp.ok:
            data = resp.json()
            if isinstance(data, dict) and "values" in data:
                from models import add_fitbit_step, get_fitbit_steps
                base = datetime.fromisoformat(data["from_timestamp"].replace("Z", "+00:00"))
                for offset, value in zip(data["offsets"], data["values"]):
                    ts = base + timedelta(milliseconds=offset)
                    add_fitbit_step(
                        uid,
                        ts.strftime("%Y-%m-%d"),
                        ts.strftime("%H:%M"),
                        int(value)
                    )
    except Exception as e:
        print("Fitbit fetch error:", e)

    # Always query from DB, never display from memory
    from models import get_fitbit_steps
    fitbit_data_db = get_fitbit_steps(uid, since_days=7)

    return render_template("fitbit.html", grouped=group_by_day(fitbit_data_db))

@dashboard_bp.route("/connect/libre")
def connect_libre():
    token = session.get("spike_token")
    if not token:
        return redirect(url_for("auth.login"))

    resp = requests.get(
        "https://app-api.spikeapi.com/v3/providers/freestyle_libre/integration/init_url",
        headers={"Authorization": f"Bearer {token}"}
    )
    if resp.ok:
        return redirect(resp.json().get("path"))
    else:
        return "Libre connection failed", 400


@dashboard_bp.route("/libre-data")
def libre_data():
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login"))

    token = session.get("spike_token")
    if not token:
        return redirect(url_for("auth.login"))

    try:
        url = "https://app-api.spikeapi.com/v3/queries/timeseries"
        headers = {"Authorization": f"Bearer {token}"}
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=1)

        params = {
            "provider_slug": "libre",
            "metric": "glucose",
            "from_timestamp": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to_timestamp": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "interval": "5minute"
        }

        resp = requests.get(url, headers=headers, params=params)
        if resp.ok:
            data = resp.json()
            if isinstance(data, dict) and "values" in data:
                from models import add_libre_glucose
                base = datetime.fromisoformat(data["from_timestamp"].replace("Z", "+00:00"))
                for offset, value in zip(data["offsets"], data["values"]):
                    ts = base + timedelta(milliseconds=offset)
                    add_libre_glucose(
                        uid,
                        ts.strftime("%Y-%m-%d"),
                        ts.strftime("%H:%M"),
                        float(value)
                    )
    except Exception as e:
        print("Libre fetch error:", e)

    from models import get_libre_glucose
        # ✨ Run the fake seeder here for this user
    seed_fake_libre(user_id=uid, days=1)

    # Then query DB for refreshed data
    backfill_libre_glucose(uid, hours=48)
    libre_data_db = get_libre_glucose(uid, hours=48)

    return render_template("libre.html", grouped=group_by_day(libre_data_db))


@dashboard_bp.route("/spike/callback")
def spike_callback():
    """
    This endpoint is called by Spike after connecting Fitbit or Libre.
    It doesn’t receive sensitive data – just indicates the connection succeeded.
    """
    provider = request.args.get("provider_slug", "a provider")
    flash(f"{provider.title()} connected successfully!", "success")
    return redirect(url_for("dashboard.dashboard"))


from collections import defaultdict

def group_by_day(rows):
    """
    Convert flat list [{date,time,steps},...] into
    { "YYYY-MM-DD": [ {...}, {...} ] }
    """
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["date"]].append(r)
    return grouped




@dashboard_bp.route("/sugar-grading")
def sugar_grading():
    uid = session.get("user_id")
    if not uid:
        return redirect(url_for("auth.login"))

    result = calculate_sugar_grade(uid, hours=48)

    if not result:
        flash("No Libre glucose data available for grading.", "error")
        return redirect(url_for("dashboard.libre_data"))

    return render_template("sugar_grading.html", result=result)