from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI()
def research_farming(question: str) -> str:
    """Search the web for reliable agriculture information."""
    question = question.strip()
    if not question:
        return "Please enter an agriculture question."
    try:
        response = client.responses.create(
            model="gpt-4.1",
            tools=[{"type": "web_search"}],
            input=(
                "You are a Smart Farming Research Assistant. "
                "Search the web for reliable agricultural sources. "
                "Prioritize FAO, agricultural universities, and "
                "government agriculture departments. "
                "Give practical advice in simple language. "
                "Include source links when available. "
                "Do not invent sources or URLs. "
                "For pesticide and chemical advice, be cautious "
                "and recommend following the product label.\n\n"
                f"Farmer's question: {question}"
            ),
            max_output_tokens=800,
        )
        return response.output_text or "No research answer was returned."
    except Exception as error:
        return f"Farming research failed: {error}"
def main():
    print("=== Smart Farming Research Assistant ===")
    question = input("Ask an agriculture question: ").strip()
    print("\nSearching agriculture websites...\n")
    print(research_farming(question))
if __name__ == "__main__":
    main()