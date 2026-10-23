from farming_tools import get_farming_tips, crop_advisor
from weather_tool import get_weather


def run_farm_assistant(crop, problem, city):
    advice = crop_advisor(crop, problem)
    tips = get_farming_tips(crop)
    weather = get_weather(city)

    report = {
        "crop": crop,
        "problem": problem,
        "advice": advice,
        "farming_tips": tips,
        "weather": weather
    }

    return report