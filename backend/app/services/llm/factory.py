from app.core.config import settings
from app.services.llm.base import LLMClient
from app.services.llm.deepseek_client import DeepSeekClient
from app.services.llm.fallback_client import FallbackClient


def get_llm_client() -> LLMClient:
    if settings.llm_api_key:
        if settings.llm_provider == "deepseek":
            return DeepSeekClient(api_key=settings.llm_api_key)
        # Future providers (gemini, claude, etc.) get added here as an
        # elif, without touching any code that calls get_llm_client().

    return FallbackClient()