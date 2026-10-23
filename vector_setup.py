from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv()
client = OpenAI()

# Step 1: Check whether the farming guide exists
file_path = Path(__file__).parent / "crop_guide.txt"

if not file_path.exists():
    raise FileNotFoundError(
        "crop_guide.txt nahi mili. "
        "Isay vector_setup.py ke same folder mein rakho."
    )

# Step 2: Upload the farming guide
with open(file_path, "rb") as file:
    uploaded_file = client.files.create(
        file=file,
        purpose="assistants",
    )

print("File uploaded successfully!")
print("File ID:", uploaded_file.id)

# Step 3: Create a vector store
vector_store = client.vector_stores.create(
    name="Smart Farming Knowledge Base"
)

print("Vector store created!")
print("Vector Store ID:", vector_store.id)

# Step 4: Add file to the vector store
client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=uploaded_file.id,
)

print("Waiting for farming guide processing...")

# Step 5: Check processing status
while True:
    file_status = client.vector_stores.files.retrieve(
        vector_store_id=vector_store.id,
        file_id=uploaded_file.id,
    )

    print("File status:", file_status.status)

    if file_status.status == "completed":
        print("SUCCESS: Farming guide is ready!")
        print("Save this Vector Store ID:", vector_store.id)
        break

    if file_status.status in ("failed", "cancelled"):
        raise RuntimeError(
            f"File processing failed: {file_status.status}"
        )

    time.sleep(2)