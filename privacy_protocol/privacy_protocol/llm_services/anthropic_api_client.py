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
                # Print only if directly run or verbose logging enabled
                if __name__ == '__main__' or os.getenv('VERBOSE_LOGGING'):
                    print("AnthropicLLMService: Anthropic client initialized successfully.")
            except Exception as e:
                print(f"AnthropicLLMService: Error initializing Anthropic client: {e}. Service will be unavailable.")
                self.key_available = False
                self.client = None
        # else: # Warning printed by is_api_key_available
        #     if __name__ == '__main__' or os.getenv('VERBOSE_LOGGING'):
        #         print("AnthropicLLMService: API Key not found. Service will be unavailable.")


    def get_api_key_env_var(self) -> str:
        return ANTHROPIC_API_KEY_ENV_VAR

    def is_api_key_available(self) -> tuple[bool, str | None]:
        key = os.environ.get(self.get_api_key_env_var())
        if not key:
            # This warning is useful when the class is instantiated.
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

            if response.content and response.content[0] and isinstance(response.content[0].text, str):
                summary = response.content[0].text.strip()
                if not summary:
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
                return summary

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

    def classify_clause(self, clause_text: str, available_categories: list[str]) -> str | None:
        if not self.key_available or not self.client:
            return None

        if not clause_text or not clause_text.strip():
            return None

        try:
            category_list_str = ", ".join([f"'{cat}'" for cat in available_categories])
            system_prompt = (
                f"You are an expert text classifier. Your task is to classify the provided privacy policy clause "
                f"into exactly one of the following categories. Respond with only the category name from this list, "
                f"and nothing else. Do not add any explanatory text before or after the category name.\n\n"
                f"Available Categories: {category_list_str}"
            )
            user_message_content = (
                f"Privacy Policy Clause to Classify:\n"
                f"\"{clause_text}\"\n\n"
                f"Category:"
            )

            response = self.client.messages.create(
                model=DEFAULT_ANTHROPIC_MODEL,
                max_tokens=50,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message_content}]
            )

            if response.content and response.content[0] and isinstance(response.content[0].text, str):
                raw_response_text = response.content[0].text.strip()
                if raw_response_text:
                    cleaned_response = raw_response_text.strip("'\"")
                    for cat in available_categories:
                        if cleaned_response.lower() == cat.lower():
                            return cat

                    print(f"Anthropic classification response ('{raw_response_text}') not an exact match. Trying substring.")
                    for cat in available_categories:
                        if cat.lower() in raw_response_text.lower():
                            return cat # Return the first substring match

                    print(f"Anthropic classification response ('{raw_response_text}') did not map to any available category.")
                    return None

            if response.stop_reason == "max_tokens" and not (response.content and response.content[0].text):
                 print(f"Anthropic API stopped due to max_tokens (no text content produced) for classification: {clause_text[:100]}...")
                 return None

            print(f"Anthropic API returned no usable content for classification: {clause_text[:100]}... Stop reason: {response.stop_reason}")
            return None

        except RateLimitError as e:
            print(f"Anthropic API rate limit exceeded during classification: {e}")
            return None
        except APIError as e:
            print(f"Anthropic API error during classification: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred with Anthropic client during classification: {e}")
            return None

if __name__ == '__main__':
    print("Anthropic LLM Service Client Script - Basic Initialization Test")
    service = AnthropicLLMService()

    # Check key availability without relying on service's internal __init__ print for this specific check
    _key_available, _ = service.is_api_key_available()
    if _key_available :
        # This print is for the __main__ block itself
        print("Anthropic API Key found by is_api_key_available(). Client should be initialized if key is valid.")
    else:
        # is_api_key_available already printed a warning
        print("Anthropic API Key not found by is_api_key_available(). Client likely not initialized.")

    if service.key_available and service.client:
        print("Anthropic service instance reports key_available=True and client exists.")
        # Test summary generation
        print("\n--- Testing generate_summary ---")
        summary_clause = "Your data is anonymized and aggregated before being used for research purposes."
        summary_category = "Data Usage"
        print(f"Clause: {summary_clause}")
        summary = service.generate_summary(summary_clause, summary_category)
        if summary: print(f"Summary: {summary}")
        else: print("Failed to get summary.")

        # Test classification
        print("\n--- Testing classify_clause ---")
        test_categories = ["Data Collection", "Data Sharing", "Security", "Other"]
        clauses_to_test = [
            ("We collect your name, email, and IP address.", "Data Collection"),
            ("Your information might be shared with our advertising partners.", "Data Sharing"),
            ("This is a very generic statement that does not fit well.", "Other")
        ]
        for clause, expected_cat in clauses_to_test:
            print(f"\nClassifying clause: \"{clause}\"")
            predicted_cat = service.classify_clause(clause, test_categories)
            print(f"  Expected: {expected_cat}, Got: {predicted_cat}")
            if predicted_cat != expected_cat:
                 print(f"  Classification MISMATCH for: {clause}")
    else:
        print("Skipping live API test in __main__ because API key is not available or client failed to initialize.")
