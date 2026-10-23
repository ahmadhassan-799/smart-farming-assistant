def check_farming_input(problem):
    # Check empty input
    if not problem or not problem.strip():
        return False, "Please enter a farming question or crop problem."

    problem = problem.lower().strip()

    unsafe_words = [
        "poison",
        "dangerous chemical",
        "mix chemicals",
        "mix chemical",
        "mix chemicals to kill",
        "kill pests",
        "kill insects",
        "kill myself"
    ]

    for word in unsafe_words:
        if word in problem:
            return False, (
                "SAFETY WARNING: This request may involve unsafe "
                "chemical use. Do not mix chemicals. Follow the "
                "product label and consult a qualified agricultural expert."
            )

    return True, "Input passed the basic safety check."