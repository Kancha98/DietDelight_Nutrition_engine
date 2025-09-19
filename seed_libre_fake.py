from datetime import datetime, timedelta
import random
from models import add_libre_glucose

def floor_to_15min(dt):
    """Round datetime down to nearest 15-minute mark (e.g. 02:48 -> 02:45)."""
    return dt.replace(minute=(dt.minute // 15) * 15, second=0, microsecond=0)

def seed_fake_libre(user_id=1, days=1):
    """
    Seed fake Libre glucose readings every 15 minutes, aligned to :00/:15/:30/:45.
    Will not replace existing rows thanks to UNIQUE(user_id,date,time).
    """
    now = floor_to_15min(datetime.now())
    start = now - timedelta(days=days)

    current = start
    inserted, skipped = 0, 0

    while current <= now:
        glucose = random.randint(80, 160)  # Fake values
        try:
            add_libre_glucose(
                user_id,
                current.strftime("%Y-%m-%d"),
                current.strftime("%H:%M"),
                glucose
            )
            inserted += 1
        except Exception:
            skipped += 1
        current += timedelta(minutes=15)

    print(f"✅ Done seeding Libre fake data for user {user_id}. Inserted={inserted}, Skipped={skipped}")

if __name__ == "__main__":
    seed_fake_libre(user_id=2, days=2)