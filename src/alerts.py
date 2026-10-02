def evaluate_alert(crop_name: str, temperature: float, humidity: float, crop_stage: str) -> str:
    crop = (crop_name or "").lower()
    stage = (crop_stage or "").lower()

    if crop in {"rice", "maize", "wheat", "banana", "papaya", "mango", "grapes", "apple"}:
        if temperature > 30 and humidity > 75 and stage in {"vegetative", "flowering", "early"}:
            return "High"
        if temperature > 27 and humidity > 65:
            return "Moderate"
        return "Low"

    if crop in {"tomato", "potato", "cabbage", "pepper"}:
        if temperature > 28 and humidity > 70:
            return "High"
        if temperature > 24 and humidity > 60:
            return "Moderate"
        return "Low"

    if crop in {"coconut", "coffee", "orange", "papaya", "mango"}:
        if temperature > 32 and humidity > 80:
            return "High"
        if temperature > 28 and humidity > 70:
            return "Moderate"
        return "Low"

    if temperature > 30 and humidity > 75:
        return "Moderate"
    return "Low"
