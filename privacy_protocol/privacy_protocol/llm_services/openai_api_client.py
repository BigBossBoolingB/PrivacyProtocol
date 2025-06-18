import os
from openai import OpenAI, APIError, RateLimitError
from .base_llm_service import LLMService

OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"

class OpenAILLMService(LLMService):
    def __init__(self):
        self.api_key: str | None = None
        self.client: OpenAI | None = None
        self.key_available: bool = False

        key_status, retrieved_key = self.is_api_key_available()
        if key_status and retrieved_key:
            self.api_key = retrieved_key
            self.key_available = True
            try:
                self.client = OpenAI(api_key=self.api_key)
                # Use a print that will only show up if __name__ == '__main__' or if verbose logging is on
                if __name__ == '__main__' or os.getenv('VERBOSE_LOGGING'):
                    print("OpenAILLMService initialized successfully with API key.")
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}. Service will be unavailable.")
                self.key_available = False
                self.client = None
        else:
            # This warning is now in is_api_key_available
            # if __name__ == '__main__' or os.getenv('VERBOSE_LOGGING'):
            #    print("OpenAILLMService: API Key not found. Service will be unavailable.")
            pass


    def get_api_key_env_var(self) -> str:
        return OPENAI_API_KEY_ENV_VAR

    def is_api_key_available(self) -> tuple[bool, str | None]:
        key = os.environ.get(self.get_api_key_env_var())
        if not key:
            # This warning is useful for users running the main script or a developer
            print(f"Warning: OpenAI API key not found in environment variable {self.get_api_key_env_var()}")
            return False, None
        return True, key

    def generate_summary(self, clause_text: str, ai_category: str) -> str | None:
        if not self.key_available or not self.client:
            return "LLM service not configured: OpenAI API key missing or client failed to load."

        if not clause_text or not clause_text.strip():
            return "The provided clause text was empty."

        try:
            system_prompt = (
                f"You are an expert at explaining complex legal text from privacy policies in simple, clear terms "
                f"for a general audience (e.g., average internet user with no legal background). "
                f"Focus on what the clause means for the user's data or privacy. Avoid legal jargon. "
                f"Do not start with phrases like 'This clause states that...' or 'This policy explains...'. Get straight to the meaning."
            )
            user_prompt = (
                f"The following privacy policy clause is primarily about '{ai_category}'. "
                f"Please explain its main implications in 1-2 short, easy-to-understand sentences: "
                f"\"{clause_text}\""
            )

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=DEFAULT_OPENAI_MODEL,
            )

            if chat_completion.choices and chat_completion.choices[0].message and chat_completion.choices[0].message.content:
                summary = chat_completion.choices[0].message.content.strip()
                if "cannot provide assistance with that request" in summary.lower() or \
                   "unable to create this image" in summary.lower():
                    print(f"OpenAI API indicated refusal for: {clause_text[:100]}...")
                    return "Could not generate summary due to content policy or other restriction."
                return summary
            else:
                print(f"OpenAI API returned no content for: {clause_text[:100]}...")
                return "Summary generation failed: No content returned."

        except RateLimitError as e:
            print(f"OpenAI API rate limit exceeded: {e}")
            return "Could not generate summary due to API rate limits."
        except APIError as e:
            print(f"OpenAI API error: {e}")
            return "Could not generate summary due to an API error."
        except Exception as e:
            print(f"An unexpected error occurred with OpenAI API client: {e}")
            return "An unexpected error occurred with OpenAI client."

    def classify_clause(self, clause_text: str, available_categories: list[str]) -> str | None:
        if not self.key_available or not self.client:
            return None # Service not configured

        if not clause_text or not clause_text.strip():
            return None # Or 'Other' if in available_categories and desired

        try:
            category_list_str = ", ".join([f"'{cat}'" for cat in available_categories])
            system_prompt = (
                f"You are an expert text classifier. Your task is to classify the provided privacy policy clause "
                f"into exactly one of the following categories. Respond with only the category name from this list, "
                f"and nothing else. Do not add any explanatory text before or after the category name.\n\n"
                f"Available Categories: {category_list_str}"
            )
            user_prompt = (
                f"Privacy Policy Clause to Classify:\n"
                f"\"{clause_text}\"\n\n"
                f"Category:"
            )

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=DEFAULT_OPENAI_MODEL, # Using the class default model
                temperature=0.1, # For more deterministic classification
                max_tokens=50 # Max length for a category name is usually short
            )

            if chat_completion.choices and chat_completion.choices[0].message and chat_completion.choices[0].message.content:
                raw_response_text = chat_completion.choices[0].message.content.strip()

                if raw_response_text:
                    # Attempt to find an exact match (case-insensitive) from available_categories
                    cleaned_response = raw_response_text.strip("'\"") # Remove potential quotes
                    for cat in available_categories:
                        if cleaned_response.lower() == cat.lower():
                            return cat

                    print(f"OpenAI classification response ('{raw_response_text}') not an exact match. Trying substring.")
                    for cat in available_categories:
                        if cat.lower() in raw_response_text.lower():
                            return cat

                    print(f"OpenAI classification response ('{raw_response_text}') did not map to any available category.")
                    return None # Or 'Other' if applicable and desired

            # Handle content filter or other issues if no content
            if chat_completion.choices and chat_completion.choices[0].finish_reason == 'content_filter':
                 print(f"OpenAI API content filter triggered for classification: {clause_text[:100]}...")
                 return None # Or specific message: "Classification failed due to content filter."

            print(f"OpenAI API returned no usable content for classification: {clause_text[:100]}...")
            return None

        except RateLimitError as e:
            print(f"OpenAI API rate limit exceeded during classification: {e}")
            return None
        except APIError as e:
            print(f"OpenAI API error during classification: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred with OpenAI client during classification: {e}")
            return None

if __name__ == '__main__':
    from unittest.mock import patch, MagicMock
    print("OpenAI LLM Service Client Script")

    service = OpenAILLMService()

    _key_available, _ = service.is_api_key_available()
    if _key_available:
        print("OpenAI API Key found. Client should be initialized.")
    else:
        print("OpenAI API Key not found. Client likely not initialized.")

    if service.key_available and service.client:
        print("Attempting a sample API call for summary...")
        # ... (summary test code from before can remain or be simplified) ...
        print("\n--- Testing classify_clause with OpenAI ---")
        test_categories = ["Data Collection", "Data Sharing", "Security", "Other"]
        clauses_to_test = [
            ("We collect your name, email, and IP address.", "Data Collection"),
            ("Your information might be shared with our advertising partners.", "Data Sharing"),
            ("This is a very generic statement that does not fit well.", "Other")
        ]
        for clause, expected_cat in clauses_to_test:
            print(f"\nClassifying clause: \"{clause}\"")
            # In __main__, actual API calls are made if key is present
            predicted_cat = service.classify_clause(clause, test_categories)
            print(f"  Expected: {expected_cat}, Got: {predicted_cat}")
            if predicted_cat != expected_cat:
                 print(f"  Classification MISMATCH for: {clause}")
    else:
        print("Skipping live API test in __main__ because API key is not available or client failed to initialize.")
