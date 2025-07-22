import sqlite3
from datetime import datetime, timedelta
import random

# Connect to SQLite DB file (or create it)
conn = sqlite3.connect("diabetes_data.db")
cursor = conn.cursor()

# Create table for diabetic measurements (every 15 minutes)
cursor.execute("""
CREATE TABLE IF NOT EXISTS diabetic_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    glucose_value REAL NOT NULL
)
""")

# Populate table with sample 24-hour data (every 15 mins = 96 readings)
start_time = datetime.strptime("2025-07-20 00:00", "%Y-%m-%d %H:%M")
for i in range(96):
    timestamp = start_time + timedelta(minutes=15 * i)
    glucose_value = random.randint(60, 200)  # Simulated data
    cursor.execute("""
        INSERT INTO diabetic_measurements (timestamp, glucose_value)
        VALUES (?, ?)
    """, (timestamp.isoformat(), glucose_value))

# Create table for Sugar Control Grading Matrix
cursor.execute("""
CREATE TABLE IF NOT EXISTS grading_matrix (
    score_min INTEGER NOT NULL,
    score_max INTEGER NOT NULL,
    grade INTEGER NOT NULL,
    interpretation TEXT NOT NULL,
    suggested_actions TEXT NOT NULL
)
""")

# Insert grading matrix values from uploaded document
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
    (0, 4, 1, "Critical", "Significant intervention; low-carb focus, avoid all high-GI foods.")
]

cursor.executemany("""
    INSERT INTO grading_matrix (score_min, score_max, grade, interpretation, suggested_actions)
    VALUES (?, ?, ?, ?, ?)
""", grading_matrix)

# Save and close connection
conn.commit()
conn.close()

print(" Database 'diabetes_data.db' created with both tables populated.")
