import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


def generate_farming_image(prompt):
    print("\n🌾 AI farming image bana raha hai...")

    response = client.images.generate(
        model="gpt-image-1.5",
        prompt=(
            "Create a realistic, educational agriculture image. "
            "Show clear details useful for farmers. "
            + prompt
        ),
        size="1024x1024"
    )

    image_data = base64.b64decode(response.data[0].b64_json)

    output_path = Path("generated_farming_image.png")
    output_path.write_bytes(image_data)

    return output_path.resolve()


if __name__ == "__main__":
    print("🌱 SMART FARMING - IMAGE GENERATION")
    prompt = input(
        "Konsi farming image banani hai? "
    ).strip()

    if prompt:
        try:
            image_path = generate_farming_image(prompt)
            print("\n✅ Image successfully ban gayi!")
            print("Image location:", image_path)
        except Exception as error:
            print("\nImage generation error:", error)