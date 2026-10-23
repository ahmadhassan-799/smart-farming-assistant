import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


def analyze_crop_image(image_path):
    image_file = Path(image_path)

    if not image_file.exists():
        return "Error: Image file nahi mili."

    allowed_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    mime_type = allowed_types.get(image_file.suffix.lower())

    if not mime_type:
        return "Please JPG, JPEG, PNG ya WEBP image use karo."

    with image_file.open("rb") as file:
        image_data = base64.b64encode(file.read()).decode("utf-8")

    print("\n🌿 AI crop ki image analyze kar raha hai...")

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are a careful agriculture assistant. "
                            "Analyze this crop image. Describe visible "
                            "symptoms, possible causes, and safe next steps. "
                            "Do not claim a certain diagnosis from an image "
                            "alone. Ask for more information if needed. "
                            "Never recommend unsafe chemical mixing. "
                            "Use simple language."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:{mime_type};base64,{image_data}"
                        ),
                    },
                ],
            }
        ],
    )

    return response.output_text


if __name__ == "__main__":
    print("🌾 SMART FARMING - CROP IMAGE ANALYSIS")
    print("--------------------------------------")

    path = input(
        "Crop image ka full path paste karo: "
    ).strip().strip('"')

    try:
        result = analyze_crop_image(path)
        print("\n🤖 AI Analysis:")
        print(result)

    except Exception as error:
        print("\nError:", error)