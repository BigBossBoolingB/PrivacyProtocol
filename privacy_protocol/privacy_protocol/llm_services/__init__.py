from .base_llm_service import LLMService
from .gemini_api_client import GeminiLLMService
from .openai_api_client import OpenAILLMService
from .llm_service_factory import get_llm_service, PROVIDER_GEMINI, PROVIDER_OPENAI, ACTIVE_LLM_PROVIDER_ENV_VAR, DEFAULT_LLM_PROVIDER # Added DEFAULT_LLM_PROVIDER

# Optional: Define a default service instance that other modules can import directly
# This can simplify imports in modules that just need the configured service.
# However, it means the factory is called upon import of this __init__.py.
# default_llm_service_instance = get_llm_service()

# Expose for easy import
__all__ = [
    "LLMService",
    "GeminiLLMService",
    "OpenAILLMService",
    "get_llm_service",
    "PROVIDER_GEMINI",
    "PROVIDER_OPENAI",
    "ACTIVE_LLM_PROVIDER_ENV_VAR",
    "DEFAULT_LLM_PROVIDER", # Added
    # "default_llm_service_instance" # if you uncomment the above instance
]
