import sqlite3
import re
import hashlib
import secrets
import hmac
import random
from datetime import datetime, date, timedelta
from config import Config
import random
from datetime import datetime, timedelta
import statistics
import pprint


def get_conn():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                dob TEXT NOT NULL,
                gender TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS fitbit_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,       -- YYYY-MM-DD
                time TEXT NOT NULL,       -- HH:MM
                steps INTEGER NOT NULL,
                UNIQUE(user_id, date, time),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS libre_glucose (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,      -- YYYY-MM-DD
                time TEXT NOT NULL,      -- HH:MM
                glucose REAL NOT NULL,
                UNIQUE(user_id, date, time),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # --- Grading Matrix table ---
        c.execute("""
            CREATE TABLE IF NOT EXISTS grading_matrix (
                score_min INTEGER NOT NULL,
                score_max INTEGER NOT NULL,
                grade INTEGER NOT NULL,
                interpretation TEXT NOT NULL,
                suggested_actions TEXT NOT NULL
            )
        """)

        # Seed grading matrix if empty
        c.execute("SELECT COUNT(*) FROM grading_matrix")
        if c.fetchone()[0] == 0:
            grading_matrix = [
                (85, 100, 10, "Excellent", "Maintain current habits, keep consistent."),
                (75, 84, 9, "Very Good", "Minor adjustments; consider maintaining low-carb options."),
                (65, 74, 8, "Good", "Small improvements, e.g., adding fiber and lean protein to meals."),
                (55, 64, 7, "Fair", "Focus on stable meal timings, avoid high-GI foods."),
                (45, 54, 6, "Satisfactory", "Begin making meal adjustments to reduce variability and spikes."),
                (35, 44, 5, "Moderate", "Moderate improvements; reduce carbs at high-variance meals."),
                (25, 34, 4, "Needs Improvement", "Reduce large spikes; add low-GI foods and consider exercise adjustments."),
                (15, 24, 3, "Poor", "Re-evaluate meal composition; replace carbs with high-quality proteins."),
                (5, 14, 2, "Very Poor", "Major changes needed; focus on protein, fiber, and activity level."),
                (0, 4, 1, "Critical", "Significant intervention; low-carb focus, avoid all high-GI foods."),
            ]
            c.executemany("""
                INSERT INTO grading_matrix (score_min, score_max, grade, interpretation, suggested_actions)
                VALUES (?, ?, ?, ?, ?)
            """, grading_matrix)
            print("🌱 Seeded grading_matrix table.")


        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_users_email ON users(email)")
        conn.commit()

        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()[0] == 0:
            create_user(
                name="Admin",
                email="admin@example.com",
                dob="1990-01-01",
                gender="Other",
                password="admin123",
                conn=conn
            )
            print("🌱 Seeded default user -> email: admin@example.com, password: admin123")


def create_user(name: str, email: str, dob: str, gender: str, password: str, conn=None):
    name = (name or "").strip()
    email = (email or "").strip().lower()
    dob = (dob or "").strip()
    gender = (gender or "").strip()

    if len(name) < 2:
        return False, "Name must be at least 2 characters."
    if not valid_email(email):
        return False, "Enter a valid email address."
    if not valid_iso_date(dob):
        return False, "Enter a valid date of birth (YYYY-MM-DD)."
    if dob > date.today().isoformat():
        return False, "Date of birth cannot be in the future."
    if gender not in ("Male", "Female", "Other", "Prefer not to say"):
        return False, "Select a valid gender option."
    if len(password or "") < 6:
        return False, "Password must be at least 6 characters."

    salt_hex = secrets.token_hex(16)
    pwd_hash = hash_password(password, salt_hex)

    close_after = False
    if conn is None:
        conn = get_conn()
        close_after = True

    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (name, email, dob, gender, password_hash, salt)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, dob, gender, pwd_hash, salt_hex))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        if close_after:
            conn.close()


def get_user_by_email(email: str):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", ((email or "").lower(),))
        return c.fetchone()


def get_user_by_id(user_id: int):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return c.fetchone()


def hash_password(password: str, salt_hex: str) -> str:
    salt_bytes = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 100_000)
    return dk.hex()


def verify_password(stored_hash: str, salt_hex: str, password: str) -> bool:
    test_hash = hash_password(password, salt_hex)
    return hmac.compare_digest(stored_hash, test_hash)


def valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def valid_iso_date(d: str) -> bool:
    try:
        datetime.strptime(d, "%Y-%m-%d")
        return True
    except Exception:
        return False
    
def add_fitbit_step(user_id: int, date: str, time: str, steps: int, conn=None):
    """
    Insert a step value if not already stored (no duplicates).
    Uses UNIQUE(user_id, date, time) constraint.
    """
    close_after = False
    if conn is None:
        conn = get_conn()
        close_after = True

    try:
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO fitbit_steps (user_id, date, time, steps)
            VALUES (?, ?, ?, ?)
        """, (user_id, date, time, steps))
        conn.commit()
    finally:
        if close_after:
            conn.close()


def get_fitbit_steps(user_id: int, since_days: int = 7):
    """
    Get stored Fitbit steps for a user over the last N days.
    Returns list of dicts {date, time, steps}.
    """
    cutoff_date = (date.today() - timedelta(days=since_days)).isoformat()
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT date, time, steps
            FROM fitbit_steps
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC, time ASC
        """, (user_id, cutoff_date))
        rows = c.fetchall()
        return [dict(r) for r in rows]
    
def add_libre_glucose(user_id: int, date: str, time: str, glucose: float, conn=None):
    """
    Insert a Libre glucose reading. Avoid duplicates by UNIQUE(user_id,date,time).
    """
    close_after = False
    if conn is None:
        conn = get_conn()
        close_after = True
    try:
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO libre_glucose (user_id, date, time, glucose)
            VALUES (?, ?, ?, ?)
        """, (user_id, date, time, glucose))
        conn.commit()
    finally:
        if close_after:
            conn.close()


def get_libre_glucose(user_id: int, hours: int = 48):
    """
    Get Libre readings for the last N hours, ordered by date/time.
    """
    cutoff_dt = datetime.now() - timedelta(hours=hours)
    cutoff_str = cutoff_dt.strftime("%Y-%m-%d %H:%M")

    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT date, time, glucose
            FROM libre_glucose
            WHERE user_id = ? AND (date || ' ' || time) >= ?
            ORDER BY date ASC, time ASC
        """, (user_id, cutoff_str))
        return [dict(r) for r in c.fetchall()]

def floor_to_15min(dt):
    """Round datetime down to nearest 15-minute mark."""
    return dt.replace(minute=(dt.minute // 15) * 15, second=0, microsecond=0)



def seed_fake_libre(user_id: int, days: int = 1, meals=None):
    """
    Generate more realistic Libre-style glucose data.
    - Baseline: 90 mg/dL
    - Meals add spikes of +20-40, decaying back in 2h
    - Save every 15 minutes
    """

    # Define typical meal times if none given
    if meals is None:
        meals = [8, 13, 19]  # breakfast 8am, lunch 1pm, dinner 7pm

    now = floor_to_15min(datetime.now())
    start = now - timedelta(days=days)
    current = start

    # baseline fasting level
    baseline = 90  
    inserted = 0

    while current <= now:
        hour = current.hour
        val = baseline

        # Add meal-driven spikes
        for meal_hr in meals:
            # if we are within 2h after a meal time
            if meal_hr <= hour < meal_hr+2:
                # simulate highest spike just after meal, then decay
                minutes_since_meal = (hour - meal_hr) * 60 + current.minute
                peak = random.randint(25, 40)  # spike magnitude
                decay = max(0, peak - (minutes_since_meal * (peak/120)))  # linear decay over 2h
                val += int(decay)

        # add tiny random jitter (+/-5 mg/dL) for realism
        val += random.randint(-5, 5)

        # store in DB
        add_libre_glucose(
            user_id,
            current.strftime("%Y-%m-%d"),
            current.strftime("%H:%M"),
            val
        )
        inserted += 1
        current += timedelta(minutes=15)

    print(f"✅ Inserted {inserted} realistic Libre readings for user {user_id}.")



import pprint   # at top of file

def calculate_sugar_grade(user_id: int, hours: int = 48):
    """
    Calculate sugar grading metrics for a given user_id over the last N hours (default: 48h).
    Reads from libre_glucose table and grading_matrix in users_web.db
    """
    with get_conn() as conn:
        c = conn.cursor()

        from_dt = datetime.now() - timedelta(hours=hours)

        c.execute("""
            SELECT glucose FROM libre_glucose
            WHERE user_id=? AND date || ' ' || time >= ?
            ORDER BY date, time
        """, (user_id, from_dt.strftime("%Y-%m-%d %H:%M")))

        rows = c.fetchall()
        glucose_values = [r[0] for r in rows]

        if not glucose_values:
            return None

        # --- all your scoring exactly as you had ---
        in_range_count = sum(1 for v in glucose_values if 70 <= v <= 150)
        tir_percent = (in_range_count / len(glucose_values)) * 100
        if tir_percent >= 90: tir_score = 100
        elif tir_percent >= 80: tir_score = 90
        elif tir_percent >= 70: tir_score = 80
        elif tir_percent >= 60: tir_score = 70
        else:
            reduction = int((60 - tir_percent) // 10) * 10
            tir_score = max(0, 70 - reduction)

        mean_glucose = statistics.mean(glucose_values)
        std_dev = statistics.stdev(glucose_values) if len(glucose_values) > 1 else 0
        cv = (std_dev / mean_glucose) * 100 if mean_glucose else 0
        if 10 <= cv <= 20: variability_score = 100
        elif 21 <= cv <= 30: variability_score = 80
        elif 31 <= cv <= 40: variability_score = 60
        elif 41 <= cv <= 50: variability_score = 40
        else: variability_score = 20

        avg_glucose = round(mean_glucose)
        if 90 <= avg_glucose <= 110: avg_score = 100
        elif 111 <= avg_glucose <= 130: avg_score = 90
        elif 131 <= avg_glucose <= 150: avg_score = 70
        elif 151 <= avg_glucose <= 170: avg_score = 50
        else: avg_score = 30

        spike_count = 0
        last = None
        for g in glucose_values:
            if last is not None and (g - last) > 30:
                spike_count += 1
            last = g

        if spike_count == 0: spike_score = 100
        elif spike_count == 1: spike_score = 80
        elif spike_count == 2: spike_score = 60
        elif spike_count == 3: spike_score = 40
        else: spike_score = 20

        final_score = round(
            (tir_score * 0.35) +
            (variability_score * 0.25) +
            (avg_score * 0.25) +
            (spike_score * 0.15)
        )

        c.execute("""
            SELECT grade, interpretation, suggested_actions
            FROM grading_matrix
            WHERE ? BETWEEN score_min AND score_max
        """, (final_score,))
        result = c.fetchone()

        if result:
            grade, interpretation, actions = result
        else:
            grade, interpretation, actions = (None, "Unknown", "No suggestions")

        # --- Build and print result dict ---
        result_dict = {
            "tir_percent": round(tir_percent, 2),
            "tir_score": tir_score,
            "variability": round(cv, 2),
            "variability_score": variability_score,
            "avg_glucose": avg_glucose,
            "avg_score": avg_score,
            "spike_count": spike_count,
            "spike_score": spike_score,
            "final_score": final_score,
            "grade": grade,
            "interpretation": interpretation,
            "suggested_actions": actions
        }

        print("\n=== Sugar Grade Calculation for user", user_id, " ===", flush=True)
        pprint.pprint(result_dict, indent=2)   # pretty output
        print("====================================================\n", flush=True)

        return result_dict
    
    

import random

def backfill_libre_glucose(user_id: int, hours: int = 48):
    """
    Ensure every 15-min slot in the last N hours exists for this user.
    Missing slots are filled with 'realistic' baseline values.
    """
    now = floor_to_15min(datetime.now())
    start = now - timedelta(hours=hours)

    current = start
    baseline = 95

    with get_conn() as conn:
        c = conn.cursor()
        while current <= now:
            date_str = current.strftime("%Y-%m-%d")
            time_str = current.strftime("%H:%M")

            # check if this slot already exists
            c.execute("""
                SELECT 1 FROM libre_glucose
                WHERE user_id=? AND date=? AND time=?
                """, (user_id, date_str, time_str))
            exists = c.fetchone()

            if not exists:
                # generate a realistic-ish glucose value
                # - stable overnight
                # - small bumps around common meals (8a, 1p, 7p)
                val = baseline + random.randint(-5, 5)
                if current.hour in (8, 9):  # breakfast spike
                    val += random.randint(20, 35)
                elif current.hour in (13, 14):  # lunch spike
                    val += random.randint(20, 40)
                elif current.hour in (19, 20):  # dinner spike
                    val += random.randint(25, 45)

                c.execute("""
                    INSERT INTO libre_glucose (user_id, date, time, glucose)
                    VALUES (?, ?, ?, ?)
                """, (user_id, date_str, time_str, val))
            current += timedelta(minutes=15)
        conn.commit()
