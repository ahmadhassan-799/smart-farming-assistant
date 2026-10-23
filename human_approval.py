def ask_farmer_approval(action):
    print("\nFARMER APPROVAL REQUIRED")
    print("Proposed action:", action)

    choice = input("Do you approve this action? (yes/no): ")

    if choice.lower().strip() == "yes":
        return "Action approved by farmer."

    return "Action not approved. No action taken."