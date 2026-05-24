from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from google import genai

load_dotenv()

# ==========================================
# TEXT / REASONING MODELS (LANGCHAIN)
# ==========================================

fast_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.3
)

pro_llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=0.5
)

critic_llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=0.2
)

creative_llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-pro-preview",
    temperature=0.8
)

# Default orchestration model
llm = fast_llm


# ==========================================
# GOOGLE GENAI SDK CLIENT
# ==========================================

genai_client = genai.Client()


# ==========================================
# IMAGE GENERATION MODELS
# ==========================================

IMAGE_MODEL_FAST = "imagen-4.0-fast-generate-001"
IMAGE_MODEL_PRO = "imagen-4.0-generate-001"


# ==========================================
# VIDEO GENERATION MODELS
# ==========================================

VIDEO_MODEL_FAST = "veo-3.0-fast-generate-001"

VIDEO_MODEL_PRO = "veo-3.1-generate-preview"


# ==========================================
# OMNI / MULTIMODAL MODELS
# ==========================================

OMNI_MODEL = "gemini-3.1-pro-preview"

LIVE_MODEL = "gemini-3.1-flash-live-preview"