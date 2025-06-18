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

if __name__ == '__main__':
    from unittest.mock import patch, MagicMock # For __main__ without prints from class
    print("OpenAI LLM Service Client Script")

    # Temporarily suppress class-level prints for cleaner __main__ output unless VERBOSE_LOGGING is set
    # The is_api_key_available print is valuable so we keep that one unless VERBOSE_LOGGING is explicitly false.

    # For the __main__ block, we want to see the "API Key not found" message if it's the case.
    # So, we don't globally patch sys.stdout here for the class instantiation.
    openai_service = OpenAILLMService()

    if openai_service.key_available and openai_service.client:
        print("OpenAI API Key found and client initialized (or mocked).")
        sample_clause = "We may share your personal information... with our advertising partners..."
        sample_category = "Data Sharing"
        print(f"\nTesting summary for category '{sample_category}':")
        print(f"Clause: {sample_clause}")
        summary = openai_service.generate_summary(sample_clause, sample_category)
        if summary:
            print(f"\nOpenAI Summary: {summary}")
        else:
            print("\nFailed to get summary from OpenAI (returned None or specific error string).")
    else:
        # This message will appear if the key isn't set in the environment for this direct run
        print("OpenAI API Key not found or client failed to initialize in __main__. Skipping live API test.")
