import os
from .base_llm_service import LLMService
from .gemini_api_client import GeminiLLMService
from .openai_api_client import OpenAILLMService
from .anthropic_api_client import AnthropicLLMService # Import Anthropic service

# Environment variable to select the active LLM provider
ACTIVE_LLM_PROVIDER_ENV_VAR = "ACTIVE_LLM_PROVIDER"
DEFAULT_LLM_PROVIDER = "gemini" # Default to Gemini if not specified

# Supported provider names (must match keys in PROVIDER_MAP)
PROVIDER_GEMINI = "gemini"
PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC = "anthropic" # Add Anthropic constant

PROVIDER_MAP = {
    PROVIDER_GEMINI: GeminiLLMService,
    PROVIDER_OPENAI: OpenAILLMService,
    PROVIDER_ANTHROPIC: AnthropicLLMService, # Add Anthropic to map
}

def get_llm_service(provider_name_override: str | None = None) -> LLMService | None:
    """
    Factory function to get an instance of the configured LLM service.

    Args:
        provider_name_override: If provided, this name will be used instead of
                                the environment variable setting.

    Returns:
        An instance of the LLMService (e.g., GeminiLLMService, OpenAILLMService),
        or None if the provider is unsupported or fails to initialize.
    """
    provider_name_to_use = provider_name_override
    if provider_name_to_use is None:
        provider_name_to_use = os.environ.get(ACTIVE_LLM_PROVIDER_ENV_VAR, DEFAULT_LLM_PROVIDER).lower()

    # This print is for operational visibility, especially during startup or debugging.
    # In tests, it might be suppressed if it's too noisy.
    print(f"LLM Service Factory: Attempting to load provider: {provider_name_to_use}")

    service_class = PROVIDER_MAP.get(provider_name_to_use)

    if service_class:
        try:
            service_instance = service_class() # Instantiate the service
            # The __init__ of each service class handles its own API key availability check and prints status.
            # We can check key_available here if we want to return None on key failure,
            # but PlainLanguageTranslator also checks this. For now, let factory return instance if class exists.
            # Example check (can be more robust if needed):
            if hasattr(service_instance, 'key_available') and not service_instance.key_available:
                 print(f"LLM Service Factory: Warning - API key for {provider_name_to_use} not available or client init failed. Service might be non-functional.")
            return service_instance
        except Exception as e:
            print(f"LLM Service Factory: Error initializing LLM service provider '{provider_name_to_use}': {e}")
            return None
    else:
        print(f"LLM Service Factory: Unsupported LLM provider specified: {provider_name_to_use}. Supported providers are: {list(PROVIDER_MAP.keys())}")
        return None

if __name__ == '__main__':
    from unittest.mock import patch # To control prints from underlying services for cleaner __main__ output

    print("Testing LLM Service Factory...")

    # Test with default (Gemini, assuming no env var is set for ACTIVE_LLM_PROVIDER by default in this test context)
    print("\n--- Testing Default Provider (Gemini) ---")
    # Suppress prints from GeminiLLMService's __init__ for this test run
    with patch('sys.stdout') as _: # Simple way to suppress for this block
        gemini_service = get_llm_service()
    if gemini_service:
        print(f"Successfully loaded default service: {type(gemini_service).__name__}")
        # Actual key availability depends on environment, which is fine for this __main__ test
        print(f"API Key available for Gemini (as per service instance): {gemini_service.key_available if hasattr(gemini_service, 'key_available') else 'N/A'}")
    else:
        print("Failed to load default Gemini service.")

    # Test with OpenAI explicitly
    print("\n--- Testing OpenAI Provider (Explicit Override) ---")
    with patch('sys.stdout') as _: # Suppress prints from OpenAILLMService's __init__
        openai_service = get_llm_service(provider_name_override=PROVIDER_OPENAI)
    if openai_service:
        print(f"Successfully loaded OpenAI service: {type(openai_service).__name__}")
        print(f"API Key available for OpenAI (as per service instance): {openai_service.key_available if hasattr(openai_service, 'key_available') else 'N/A'}")
    else:
        print("Failed to load OpenAI service.")

    # Test with an unsupported provider
    print("\n--- Testing Unsupported Provider ---")
    unsupported_service = get_llm_service(provider_name_override="unsupported_provider")
    if unsupported_service is None:
        print("Correctly handled unsupported provider (returned None).")
    else:
        print(f"Error: Unexpectedly loaded service for unsupported provider: {type(unsupported_service).__name__}")

    # Test with environment variable override
    print("\n--- Testing Provider from Environment Variable (OpenAI) ---")
    with patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_OPENAI}):
        with patch('sys.stdout') as _:
            env_service = get_llm_service()
        if env_service:
            print(f"Successfully loaded service from ENV_VAR: {type(env_service).__name__} (expected OpenAI)")
                # self.assertIsInstance(env_service, OpenAILLMService) # This line is for unittest
        else:
            print("Failed to load service from ENV_VAR.")

    print("\n--- Testing Provider from Environment Variable (Gemini) ---")
    with patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}):
        with patch('sys.stdout') as _:
            env_service_gemini = get_llm_service()
        if env_service_gemini:
            print(f"Successfully loaded service from ENV_VAR: {type(env_service_gemini).__name__} (expected Gemini)")
            print(f"  Key available: {env_service_gemini.key_available if hasattr(env_service_gemini, 'key_available') else 'N/A'}")
        else:
            print("Failed to load service from ENV_VAR (Gemini).")

    print("\n--- Testing Anthropic Provider (Explicit Override) ---")
    with patch('sys.stdout') as _: # Suppress prints from AnthropicLLMService's __init__
        anthropic_service = get_llm_service(provider_name_override=PROVIDER_ANTHROPIC)
    if anthropic_service:
        print(f"Successfully loaded Anthropic service: {type(anthropic_service).__name__}")
        print(f"API Key available for Anthropic (as per service instance): {anthropic_service.key_available if hasattr(anthropic_service, 'key_available') else 'N/A'}")
    else:
        print("Failed to load Anthropic service.")
