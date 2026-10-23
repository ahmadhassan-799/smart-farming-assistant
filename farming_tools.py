def get_farming_tips(crop):
    crop = crop.lower()

    if crop == "wheat":
        return "Check soil moisture and monitor the field regularly."
    elif crop == "rice":
        return "Manage water carefully and monitor pests."
    elif crop == "cotton":
        return "Inspect the crop regularly for pests."
    else:
        return "Check soil moisture and consult local farming experts."


def crop_advisor(crop, problem):
    problem = problem.lower()

    if "yellow" in problem:
        return "Yellow leaves may be caused by nutrient deficiency, excess water, or disease."
    elif "water" in problem or "dry" in problem:
        return "Check soil moisture before watering."
    elif "insect" in problem or "pest" in problem:
        return "Inspect the crop and identify the pest before choosing treatment."
    else:
        return "More details about the symptoms are needed."