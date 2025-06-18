import os
from anthropic import Anthropic, APIError, RateLimitError
from .base_llm_service import LLMService

ANTHROPIC_API_KEY_ENV_VAR = "ANTHROPIC_API_KEY"
DEFAULT_ANTHROPIC_MODEL = "claude-3-sonnet-20240229"

class AnthropicLLMService(LLMService):
    def __init__(self):
        self.api_key: str | None = None
        self.client: Anthropic | None = None
        self.key_available: bool = False

        key_status, retrieved_key = self.is_api_key_available()
        if key_status and retrieved_key:
            self.api_key = retrieved_key
            self.key_available = True
            try:
                self.client = Anthropic(api_key=self.api_key)
            except Exception as e:
                print(f"AnthropicLLMService: Error initializing Anthropic client: {e}. Service will be unavailable.")
                self.key_available = False
                self.client = None

    def get_api_key_env_var(self) -> str:
        return ANTHROPIC_API_KEY_ENV_VAR

    def is_api_key_available(self) -> tuple[bool, str | None]:
        key = os.environ.get(self.get_api_key_env_var())
        if not key:
            print(f"Warning: Anthropic API key not found in environment variable {self.get_api_key_env_var()}")
            return False, None
        return True, key

    def generate_summary(self, clause_text: str, ai_category: str) -> str | None:
        if not self.key_available or not self.client:
            return "LLM service not configured: Anthropic API key missing or client failed to load."

        if not clause_text or not clause_text.strip():
            return "The provided clause text was empty."

        try:
            system_prompt = (
                f"You are an expert at explaining complex legal text from privacy policies in simple, clear terms "
                f"for a general audience (e.g., average internet user with no legal background). "
                f"Focus on what the clause means for the user's data or privacy. Avoid legal jargon. "
                f"Do not start with phrases like 'This clause states that...' or 'This policy explains...'. Get straight to the meaning. "
                f"The policy clause you are explaining is primarily about '{ai_category}'."
            )
            user_message = (
                f"Please explain the main implications of the following privacy policy clause in 1-2 short, easy-to-understand sentences: "
                f"\"{clause_text}\""
            )

            response = self.client.messages.create(
                model=DEFAULT_ANTHROPIC_MODEL,
                max_tokens=250,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            # Revised logic for handling response
            if response.content and response.content[0] and isinstance(response.content[0].text, str):
                summary = response.content[0].text.strip()

                if not summary: # Handles case where .text exists but is empty or whitespace after strip
                    print(f"Anthropic API returned empty text content for: {clause_text[:100]}... Stop reason: {response.stop_reason}")
                    return "Summary generation failed: Empty content returned."

                refusal_patterns = [
                    "sorry, but i cannot provide assistance with that request",
                    "i am unable to help with that request"
                ]
                for pattern in refusal_patterns:
                    if pattern in summary.lower():
                        print(f"Anthropic API indicated refusal for: {clause_text[:100]}...")
                        return "Could not generate summary due to content policy or other restriction from the AI."

                if response.stop_reason == "max_tokens":
                    print(f"Anthropic API stopped due to max_tokens for: {clause_text[:100]}...")
                    return summary + "... (summary might be truncated due to length limits)"

                # If not a refusal and not explicitly max_tokens with content (or other handled stop_reason),
                # and content is present, return it. (e.g. stop_reason == "end_turn")
                return summary

            # Fallback for cases where response.content or response.content[0].text is not as expected
            # or if there's a stop_reason without actual text content.
            if response.stop_reason == "max_tokens":
                print(f"Anthropic API stopped due to max_tokens (no text content found) for: {clause_text[:100]}...")
                return "Summary generation was stopped due to length limits (no content)."
            else:
                print(f"Anthropic API returned no text content or unexpected structure for: {clause_text[:100]}... Stop reason: {response.stop_reason}")
                return "Summary generation failed: No usable content returned."

        except RateLimitError as e:
            print(f"Anthropic API rate limit exceeded: {e}")
            return "Could not generate summary due to API rate limits."
        except APIError as e:
            print(f"Anthropic API error: {e}")
            return "Could not generate summary due to an API error from the provider."
        except Exception as e:
            print(f"An unexpected error occurred with Anthropic API client: {e}")
            return "An unexpected error occurred with Anthropic client."

if __name__ == '__main__':
    from unittest.mock import patch, MagicMock
    print("Anthropic LLM Service Client Script - Basic Initialization Test")

    # Suppress class init prints for cleaner __main__ unless VERBOSE_LOGGING is set
    with patch('sys.stdout', new_callable=MagicMock) as mock_stdout_init_check:
        # Check actual key status without init prints from the class constructor for this check
        _temp_service_for_key_check = anthropic_api_client.AnthropicLLMService()
        _key_available_for_main, _ = _temp_service_for_key_check.is_api_key_available()
        # Restore stdout for the actual service init we want to observe for __main__

    service = AnthropicLLMService() # This will use real os.environ and print its own warnings

    if service.key_available and service.client:
        print("Anthropic API Key found and client initialized for __main__.")
        sample_clause = "Your data is anonymized and aggregated before being used for research purposes."
        sample_category = "Data Usage"
        print(f"\nTesting summary generation for category '{sample_category}':")
        print(f"Clause: {sample_clause}")
        summary = service.generate_summary(sample_clause, sample_category)
        if summary:
            print(f"\nAnthropic Summary: {summary}")
        else:
            print("\nFailed to get summary from Anthropic (returned None or specific error string).")
    else:
        print("Anthropic client not initialized or key not found in __main__. Skipping live API test.")
