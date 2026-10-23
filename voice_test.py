from openai import OpenAI
from dotenv import load_dotenv
import sounddevice as sd
import soundfile as sf
import numpy as np
import io

load_dotenv()
client = OpenAI()

print("AI awaaz bana raha hai...")

with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input="Hello farmer! Your Smart Farming Assistant is ready.",
    response_format="wav"
) as response:
    audio_bytes = b"".join(response.iter_bytes())

audio, sample_rate = sf.read(io.BytesIO(audio_bytes), dtype="float32")

print("AI ka jawab speakers par suno!")
sd.play(audio, sample_rate)
sd.wait()

print("Voice test complete!")