from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()
writer_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1,
    api_key=os.getenv("GOOGLE_API_KEY")
)

IMAGE_MODEL_FAST = "imagen-4.0-fast-generate-001"
IMAGE_MODEL_PRO = "imagen-4.0-generate-001"

VIDEO_MODEL_FAST = "veo-3.0-fast-generate-001"

VIDEO_MODEL_PRO = "veo-3.1-generate-preview"

OMNI_MODEL = "gemini-3.1-pro-preview"

LIVE_MODEL = "gemini-3.1-flash-live-preview"