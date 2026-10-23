from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

load_dotenv()
client = OpenAI()

# Tumhari PDF ka exact path
pdf_path = Path(r"C:\corvit recordings\wheat_guide.pdf")

try:
    if not pdf_path.exists():
        print("PDF file nahi mili. Path check karo.")
    else:
        print("PDF mil gayi. Upload ho rahi hai...")

        # PDF upload karo
        with pdf_path.open("rb") as file:
            uploaded_file = client.files.create(
                file=file,
                purpose="assistants"
            )

        print("PDF uploaded. Vector Store ban raha hai...")

        # Naya vector store banao
        vector_store = client.vector_stores.create(
            name="Smart Farming Wheat Guide"
        )

        # PDF ko vector store mein add karke processing ka wait karo
        result = client.vector_stores.files.create_and_poll(
            vector_store_id=vector_store.id,
            file_id=uploaded_file.id
        )

        print("\nPDF processing status:", result.status)

        if result.status == "completed":
            print("SUCCESS! PDF Vector Database mein ready hai.")
            print("Nayi Vector Store ID:", vector_store.id)
            print("Is ID ko copy karke safe rakhna.")
        else:
            print("PDF process nahi hui.")
            print("Error:", result.last_error)

except Exception as error:
    print("\nUpload error:", error)