import asyncio
from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    function_tool,
    WebSearchTool,
    FileSearchTool,
)
from openai.types.responses import ResponseTextDeltaEvent
from farming_tools import get_farming_tips, crop_advisor
from weather_tool import get_weather
from memory_store import (
    save_farmer_data,
    get_farmer_data,
    save_chat_history,
    get_chat_history,
)
from guardrails import check_farming_input
from human_approval import ask_farmer_approval
load_dotenv()
# ---------------------------------
# 1. FARMING TOOLS
# ---------------------------------
@function_tool
def farming_tips_tool(crop: str) -> str:
    """Give general farming tips for a crop."""
    return str(get_farming_tips(crop))
@function_tool
def crop_advisor_tool(crop: str, problem: str) -> str:
    """Suggest possible causes and safe next steps for crop problems."""
    return str(crop_advisor(crop, problem))
@function_tool
def weather_tool(city: str) -> str:
    """Get weather information for a city."""
    return str(get_weather(city))
# ---------------------------------
# 2. CROP PROBLEM SPECIALIST AGENT
# ---------------------------------
crop_problem_agent = Agent(
    name="Crop Problem Specialist",
    instructions="""
You are an agriculture specialist.
Help farmers understand crop problems such as:
- Yellow leaves
- Dry leaves
- Insects and pests
- Possible plant diseases
- Water-related problems
Use farming tools when appropriate.
Do not claim a definite diagnosis from symptoms alone.
Ask for more details when needed.
Give safe, practical advice in English, Urdu, or Roman Urdu,
according to the farmer's language.
Do not invent chemical doses.
""",
    tools=[
        farming_tips_tool,
        crop_advisor_tool,
    ],
)
# ---------------------------------
# 3. VECTOR DATABASE
# ---------------------------------
# IMPORTANT:
# Replace this with the latest Vector Store ID printed by vector_setup.py.
VECTOR_STORE_ID = "vs_6ada746ac688819189a52efc583114b6"
# ---------------------------------
# 4. MAIN FARMING AGENT
# ---------------------------------
farm_agent = Agent(
    name="Smart Farming Assistant",
    instructions="""
You are a helpful Smart Farming Assistant.
Your job is to help farmers with:
- Crop advice
- Farming tips
- Crop problems
- Weather information
- General agriculture questions
Rules:
1. Reply in the farmer's language when possible.
2. Use farming tools when they can help.
3. Use web search for current agriculture information when needed.
4. Search the uploaded farming guide when relevant.
5. Hand off crop diagnosis questions to Crop Problem Specialist.
6. Be careful with pesticide, fertilizer and chemical recommendations.
7. Never invent chemical doses.
8. If symptoms are unclear, ask follow-up questions.
9. Do not claim you physically inspected a field.
10. Give clear, beginner-friendly answers.
""",
    tools=[
        farming_tips_tool,
        crop_advisor_tool,
        weather_tool,
        WebSearchTool(),
        FileSearchTool(vector_store_ids=[VECTOR_STORE_ID]),
    ],
    handoffs=[crop_problem_agent],
)
# ---------------------------------
# 5. STREAMING RESPONSE
# ---------------------------------
async def stream_agent_response(question: str) -> str:
    print("\n🌱 Smart Farming Assistant is thinking...\n")
    result = Runner.run_streamed(
        farm_agent,
        input=question,
    )
    full_response = ""
    async for event in result.stream_events():
        if event.type == "agent_updated_stream_event":
            print(
                f"\n[Active agent: {event.new_agent.name}]\n"
            )
        elif event.type == "raw_response_event":
            if isinstance(
                event.data,
                ResponseTextDeltaEvent,
            ):
                delta = event.data.delta
                print(delta, end="", flush=True)
                full_response += delta
    print("\n")
    return full_response
# ---------------------------------
# 6. CHECK IF APPROVAL IS NEEDED
# ---------------------------------
def needs_human_approval(answer: str) -> bool:
    """
    Ask for approval only when the answer discusses
    potentially risky or consequential farming actions.
    Ordinary informational answers do not need approval.
    """
    risk_words = [
        "pesticide",
        "insecticide",
        "herbicide",
        "fungicide",
        "chemical spray",
        "spray dose",
        "chemical dosage",
        "fertilizer dose",
        "fertiliser dose",
        "high concentration",
        "strong chemical",
        "stop irrigation",
        "major irrigation change",
    ]
    answer_lower = answer.lower()
    return any(word in answer_lower for word in risk_words)
# ---------------------------------
# 7. MAIN PROGRAM
# ---------------------------------
async def main():
    print("=" * 45)
    print("🌱 SMART FARMING ASSISTANT")
    print("=" * 45)
    farmer_id = input("\nEnter your farmer ID or email: ").strip()
    if not farmer_id:
        print("Please enter a farmer ID or email.")
        return
    print(
        "\nAssalam-o-Alaikum! Ask me anything about farming."
    )
    print("Type 'exit' to close the assistant.\n")
    while True:
        problem = input("You: ").strip()
        if problem.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using Smart Farming Assistant!")
            break
        if not problem:
            continue
        # Guardrails
        try:
            safety_result = check_farming_input(problem)
            if safety_result is False:
                print(
                    "\nAssistant: I need a safe, "
                    "farming-related question to help you.\n"
                )
                continue
            if isinstance(safety_result, str) and safety_result.strip():
                # If the guardrail returns a warning/message,
                # display it only when it indicates rejection.
                warning = safety_result.lower()
                if any(
                    word in warning
                    for word in [
                        "blocked",
                        "not allowed",
                        "unsafe",
                        "reject",
                    ]
                ):
                    print(f"\nAssistant: {safety_result}\n")
                    continue
        except Exception as error:
            print(f"\nGuardrail check issue: {error}")
            print("Continuing with caution.\n")
        # Load farmer memory and previous history
        try:
            farmer_data = get_farmer_data(farmer_id)
        except Exception:
            farmer_data = None
        try:
            chat_history = get_chat_history(farmer_id)
        except Exception:
            chat_history = None
        context = f"""
Farmer ID: {farmer_id}
Previously saved farmer information:
{farmer_data}
Previous conversation history:
{chat_history}
Current farmer question:
{problem}
Answer the current question clearly. Use previous information
only when it is relevant.
"""
        # Run the streaming agent
        try:
            answer = await stream_agent_response(context)
        except Exception as error:
            print(f"\nSomething went wrong: {error}\n")
            continue
        # Save chat history
        try:
            save_chat_history(
                farmer_id,
                problem,
                answer,
            )
        except Exception as error:
            print(f"\nChat history could not be saved: {error}")
        # Ask approval only for potentially risky advice
        if answer and needs_human_approval(answer):
            print(
                "\n⚠️ This answer includes a potentially "
                "important farming recommendation."
            )
            try:
                ask_farmer_approval()
            except Exception as error:
                print(
                    "\nApproval step could not be completed: "
                    f"{error}"
                )
        # Save useful farmer information
        try:
            save_farmer_data(
                farmer_id,
                {
                    "last_question": problem,
                    "last_answer": answer,
                },
            )
        except Exception as error:
            print(f"\nFarmer memory could not be saved: {error}")
        print("\n" + "-" * 45 + "\n")
if __name__ == "__main__":
    asyncio.run(main())