from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)

# Free to use for 14,4k requests per day
gemma_3_27b = ChatGoogleGenerativeAI(
    model="gemma-3-27b-it",
    api_key=settings.GEMINI_API_KEY,
    temperature=0.0,
)
try:
    gemma_3_27b.invoke("Hello")
    logger.info("Gemma 3:27b is working")
except Exception as e:
    logger.error(f"Error connecting to Google Generative AI: {e}")


# # Free to use for 250 requests per day
# gemini_2_5_flash = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     api_key=settings.GEMINI_API_KEY,
#     temperature=0.0,
# )
# try:
#     gemini_2_5_flash.invoke("Hello")
#     logger.info("Gemini 2.5 Flash is working")
# except Exception as e:
#     logger.error(f"Error connecting to Google Generative AI: {e}")

local_model = ChatOllama(model="gemma3:12b", temperature=0.0)
