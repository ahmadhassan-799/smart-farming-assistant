import asyncio
import io

import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from openai import OpenAI
from agents import Runner

from ai_agent import farm_agent

load_dotenv()
client = OpenAI()

SAMPLE_RATE = 16000
MIC_DEVICE = 1


async def main():
    print("\n🌾 SMART FARMING VOICE ASSISTANT")
    print("=" * 35)

    while True:
        command = input(
            "\nEnter dabao aur bolna shuru karo "
            "(exit likho band karne ke liye): "
        ).strip()

        if command.lower() == "exit":
            print("Allah Hafiz, Farmer! 🌾")
            break

        print("\n🎤 5 seconds tak apni farming problem bolo...")

        try:
            recording = sd.rec(
                int(5 * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
                device=MIC_DEVICE
            )
            sd.wait()

            wav_buffer = io.BytesIO()
            sf.write(
                wav_buffer,
                recording,
                SAMPLE_RATE,
                format="WAV"
            )
            wav_buffer.seek(0)
            wav_buffer.name = "farmer_question.wav"

            print("\n📝 Tumhari awaaz samajh raha hoon...")

            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=wav_buffer
            )

            question = transcript.text.strip()

            if not question:
                print("Awaaz samajh nahi aayi. Dobara try karo.")
                continue

            print("\nTumhara sawal:", question)
            print("\n🤖 AI jawab tayyar kar raha hai...")

            result = await Runner.run(
                farm_agent,
                input=question
            )
            answer = result.final_output

            print("\n🌾 Smart Farming Assistant:")
            print(answer)

            print("\n🔊 AI ka jawab suno...")

            with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=str(answer),
                response_format="wav"
            ) as response:
                audio_bytes = b"".join(response.iter_bytes())

            audio, rate = sf.read(
                io.BytesIO(audio_bytes),
                dtype="float32"
            )

            sd.play(audio, rate)
            sd.wait()

            print("\n✅ Ho gaya! Dobara sawal pooch sakte ho.")

        except Exception as error:
            print("\n❌ Error:", error)


if __name__ == "__main__":
    asyncio.run(main())