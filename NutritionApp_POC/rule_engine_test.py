import json

# 🔹 Sample input data for testing
glucose_readings = [
    {"glucose_value": 70}

]

steps = 5600  # Daily step count

meals_json = [
    {"name": "Brown Rice Bowl", "carbs": 60},
    {"name": "Fruit Smoothie", "carbs": 45},
    {"name": "Pasta with Veggies", "carbs": 75}
]


# 🔍 Logic functions
def is_diabetic(glucose_reading: list) -> bool:
    for result in glucose_reading:
        if result.get("glucose_value") > 80:
            print("🔴 User is diabetic")
            return True
    print("🟢 User is not diabetic")
    return False


def classify_activity(steps: int) -> str:
    if steps < 5000:
        return "low"
    elif steps < 10000:
        return "moderate"
    else:
        return "high"


def get_carb_modifier(is_diabetic: bool, activity_level: str) -> float:
    if not is_diabetic:
        return 1.0
    return {
        "low": 0.70,
        "moderate": 0.80,
        "high": 0.90
    }[activity_level]


def adjust_meals_for_user(glucose_reading: list, steps: int, meals_json: list) -> list:
    diabetic = is_diabetic(glucose_reading)
    activity_level = classify_activity(steps)
    print(f"📊 Activity Level: {activity_level}")
    modifier = get_carb_modifier(diabetic, activity_level)
    print(f"🍽️ Carb Modifier: {modifier}")

    adjusted_meals = []
    for meal in meals_json:
        original_carbs = meal["carbs"]
        adjusted_carbs = round(original_carbs * modifier, 1)
        adjusted_meals.append({
            "name": meal["name"],
            "original_carbs": original_carbs,
            "adjusted_carbs": adjusted_carbs,
            "portion_size": modifier
        })

    return adjusted_meals


# 🧪 Run test
result = adjust_meals_for_user(glucose_readings, steps, meals_json)
print("\n✅ Adjusted Meal Recommendations:")
print(json.dumps(result, indent=2))
