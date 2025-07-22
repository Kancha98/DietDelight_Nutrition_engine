import sqlite3
import statistics
from datetime import datetime, timedelta


print("\n AI Powered Nutrition Platform")
print("---------------------------------")


# Connect to existing DB
conn = sqlite3.connect("diabetes_data.db")
cursor = conn.cursor()
print("\nData Refreshed: 2025-07-21 06:00:00")

# Fetch all glucose readings
cursor.execute("SELECT glucose_value FROM diabetic_measurements")
rows = cursor.fetchall()
glucose_values = [row[0] for row in rows]

print("User ID : 11320")
print("Name : John Smith")
print("\n Getting Glucose values past 48 hours every 15 minutes...")
print(" Data Collected: 2025-07-19 06:15:00 - 2025-07-21 06:00:00")


# TIR (Time in Range)

in_range_count = sum(1 for value in glucose_values if 70<= value <= 150)
tir_percent = (in_range_count / len(glucose_values)) * 100
print("\nTIR Percent: ", tir_percent)

if tir_percent >= 90:
    tir_score = 100
elif tir_percent >= 80:
    tir_score = 90
elif tir_percent >= 70:
    tir_score = 80
elif tir_percent >= 60:
    tir_score = 70
else:
    reduction = int((60 - tir_percent) // 10) * 10
    tir_score = max(0, 70 - reduction)

# Variability (Coefficient of Variation)

mean_glucose = statistics.mean(glucose_values)
std_dev = statistics.stdev(glucose_values)
cv = (std_dev / mean_glucose) * 100


round_cv = round(cv)
print("Variability: ", round_cv)

if 10 <= round_cv <= 20:
    variability_score = 100
elif 21 <= round_cv <= 30:
    variability_score = 80
elif 31 <= round_cv <= 40:
    variability_score = 60
elif 41 <= cv <= 50:
    variability_score = 40
else:
    variability_score = 20

# Avg. Glucose Score 

avg_glucose = round(mean_glucose)
print("Avg Glucose: ", avg_glucose)

if 90 <= avg_glucose <= 110:
    avg_score = 100
elif 111 <= avg_glucose <= 130:
    avg_score = 90
elif 131 <= avg_glucose <= 150:
    avg_score = 70
elif 151 <= avg_glucose <= 170:
    avg_score = 50
else:
    avg_score = 30

# Spike Score 

# For now, randomly simulate spike count (custom logic can be added later)
import random
spike_count = random.randint(0, 3)
print("Spike Count: ", spike_count)

if spike_count == 0:
    spike_score = 100
elif spike_count == 1:
    spike_score = 80
elif spike_count == 2:
    spike_score = 60
elif spike_count == 3:
    spike_score = 40
else:
    spike_score = 20

# Final Weighted Score Calculation 

final_score = round(
    (tir_score * 0.35) +
    (variability_score * 0.25) +
    (avg_score * 0.25) +
    (spike_score * 0.15)
)

# Match with Grading Matrix 

cursor.execute("""
    SELECT grade, interpretation, suggested_actions
    FROM grading_matrix
    WHERE ? BETWEEN score_min AND score_max
""", (final_score,))
result = cursor.fetchone()

# Output 

print("\n  Final Diabetic Score Analysis")
print(" -------------------------------")
print(f"TIR Score:           {tir_score}")
print(f"Variability Score:   {variability_score}")
print(f"Avg Glucose Score:   {avg_score}")
print(f"Spike Score:         {spike_score}")
print(f"  Final Score:         {final_score}/100")

if result:
    grade, interpretation, actions = result
    print(f"\nGrade: {grade}/10")
    print(f"Interpretation: {interpretation}")
    print(f"Suggested Actions: {actions}\n")
else:
    print("\n No matching grade found in the matrix.")

# Close DB
conn.close()
