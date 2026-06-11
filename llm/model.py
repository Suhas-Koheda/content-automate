from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()
writer_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.1,
    api_key=os.getenv("GOOGLE_API_KEY")
)
client=genai.Client()
# chat = client.chats.create(
#     model="gemini-3.1-flash-image",
#     config=types.GenerateContentConfig(
#         response_modalities=['TEXT', 'IMAGE'],
#         tools=[{"google_search": {}}]
#     )
# )

VIDEO_MODEL_FAST = "veo-3.0-fast-generate-001"

VIDEO_MODEL_PRO = "veo-3.1-generate-preview"

OMNI_MODEL = "gemini-3.1-pro-preview"

LIVE_MODEL = "gemini-3.1-flash-live-preview"