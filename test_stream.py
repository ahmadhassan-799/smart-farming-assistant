import asyncio
from dotenv import load_dotenv
from agents import Runner
from ai_agent import farm_agent
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()

async def main():
    result = Runner.run_streamed(
        farm_agent,
        input="Rice ki fasal ke liye 3 farming tips Roman Urdu mein batao."
    )

    async for event in result.stream_events():
        if (
            event.type == "raw_response_event"
            and isinstance(event.data, ResponseTextDeltaEvent)
        ):
            print(event.data.delta, end="", flush=True)

    print("\n\nStreaming test complete.")

if __name__ == "__main__":
    asyncio.run(main())