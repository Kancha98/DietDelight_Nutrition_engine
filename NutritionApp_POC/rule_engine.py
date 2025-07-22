import json


def is_diabetic(glucose_reading: list) -> bool:
    for result in glucose_reading:
        if result.get("glucose_value") > 80:
            return True
            print("User is diabetic")
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
    modifier = get_carb_modifier(diabetic, activity_level)

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
