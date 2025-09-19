from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import get_user_by_email, create_user, verify_password
from spike_client import SpikeClient
from config import Config

auth_bp = Blueprint("auth", __name__)

spike = SpikeClient(Config.SPIKE_APP_ID, Config.SPIKE_HMAC_KEY)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = get_user_by_email(email)
        if not email or not password:
            flash("Please enter both email and password.", "error")
        elif user and verify_password(user["password_hash"], user["salt"], password):
            session["user_id"] = user["user_id"]

            try:
                token = spike.get_access_token(str(user["user_id"]))
                session["spike_token"] = token
            except Exception as e:
                flash(f"Spike token error: {e}", "error")

            flash(f"Welcome, {user['name']}!", "success")
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("dashboard.dashboard"))

    form_vals = {"name": "", "email": "", "dob": "", "gender": "Other"}
    if request.method == "POST":
        form_vals.update({
            "name": (request.form.get("name") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "dob": (request.form.get("dob") or "").strip(),
            "gender": (request.form.get("gender") or "").strip()
        })
        pw = request.form.get("password") or ""
        pw2 = request.form.get("confirm") or ""

        if pw != pw2:
            flash("Passwords do not match.", "error")
        else:
            ok, err = create_user(
                name=form_vals["name"],
                email=form_vals["email"],
                dob=form_vals["dob"],
                gender=form_vals["gender"],
                password=pw
            )
            if ok:
                flash("Account created. You can now sign in.", "success")
                return redirect(url_for("auth.login"))
            else:
                flash(err or "Registration failed.", "error")

    return render_template("register.html", f=form_vals)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Signed out.", "success")
    return redirect(url_for("auth.login"))