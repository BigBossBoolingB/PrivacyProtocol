import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from .base_llm_service import LLMService # Corrected import

GEMINI_API_KEY_ENV_VAR = "GEMINI_API_KEY"
DEFAULT_GEMINI_MODEL = 'gemini-pro'

class GeminiLLMService(LLMService):
    """
    LLMService implementation for Google's Gemini API.
    """
    def __init__(self):
        self.api_key_is_present, self.api_key = self.is_api_key_available()
        self.model = None
        if self.api_key_is_present and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
                print(f"GeminiLLMService initialized. API Key available: True. Model: {DEFAULT_GEMINI_MODEL}")
            except Exception as e:
                print(f"Error during GeminiLLMService initialization or model loading: {e}")
                self.api_key_is_present = False # Mark as unavailable if model init fails
                self.model = None
        else:
            # This print is now handled by is_api_key_available if key is None
            # print(f"GeminiLLMService initialized. API Key available: False.")
            pass


    def get_api_key_env_var(self) -> str:
        return GEMINI_API_KEY_ENV_VAR

    def is_api_key_available(self) -> tuple[bool, str | None]:
        key = os.environ.get(self.get_api_key_env_var())
        if not key:
            print(f"Warning: Gemini API key not found in environment variable {self.get_api_key_env_var()}")
            return False, None
        return True, key

    def generate_summary(self, clause_text: str, ai_category: str) -> str | None:
        if not self.api_key_is_present or not self.model:
            # print("Error: GeminiLLMService not configured (API key missing or model not loaded). Cannot generate summary.")
            # Return a specific message that can be distinguished from a successful empty summary or actual API failure
            return "LLM service not configured: API key for Gemini is missing or model failed to load."

        if not clause_text or not clause_text.strip():
            return "The provided clause text was empty."

        try:
            prompt = (
                f"You are an expert at explaining complex legal text from privacy policies in simple, clear terms "
                f"for a general audience (e.g., average internet user with no legal background). "
                f"The following privacy policy clause is primarily about '{ai_category}'. "
                f"Please explain its main implications in 1-2 short, easy-to-understand sentences. "
                f"Focus on what it means for the user's data or privacy. Avoid legal jargon in your explanation. "
                f"Do not start with phrases like 'This clause states that...' or 'This policy explains...'. Get straight to the meaning. "
                f"Clause to explain: "
                f"\"{clause_text}\""
            )

            generation_config = genai.types.GenerationConfig(
                candidate_count=1,
            )

            response = self.model.generate_content(prompt, generation_config=generation_config)

            if response.parts:
                if hasattr(response, 'text') and response.text:
                    return response.text.strip()
                elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text.strip()
                else:
                    # This case might indicate an unexpected successful response structure
                    print("Warning: Gemini API response structure not as expected or empty (but parts exist).")
                    return None
            else:
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    # print(f"Warning: Prompt blocked by Gemini API due to: {response.prompt_feedback.block_reason}")
                    return f"Could not generate summary due to safety settings (Reason: {response.prompt_feedback.block_reason})."
                # print("Warning: Gemini API returned no content parts and no specific block reason.")
                return None # Or a specific message like "No summary generated"

        except google_exceptions.GoogleAPIError as e:
            print(f"Error calling Gemini API: {e}")
            return f"Error calling Gemini API: {type(e).__name__}" # Return type of error for clarity
        except Exception as e:
            print(f"An unexpected error occurred with GeminiLLMService: {e}")
            return f"An unexpected error occurred: {type(e).__name__}"


if __name__ == '__main__':
    print("GeminiLLMService Direct Test Script")

    service = GeminiLLMService() # Initialization messages will be printed here

    if service.api_key_is_present and service.model:
        print("GeminiLLMService appears to be configured. Proceeding with test calls.")
        sample_clause = "We may share your personal information, including your browsing history and purchase records, with our advertising partners to display targeted advertisements to you on other websites."
        sample_category = "Data Sharing"
        print(f"\nTesting summary generation for category '{sample_category}':")
        print(f"Clause: {sample_clause}")
        summary = service.generate_summary(sample_clause, sample_category)
        if summary:
            print(f"\nGemini Summary: {summary}")
        else:
            print("\nFailed to get summary from Gemini (or it returned None).")

        print("\nTesting with empty clause:")
        summary_empty = service.generate_summary("", "Data Collection")
        print(f"Summary for empty clause: {summary_empty}")

        # Test blocked prompt scenario (example, might not actually trigger blocking without a real harmful prompt)
        # For a real test of blocking, you'd need a prompt that reliably gets blocked.
        # This is more to show how the error message might look.
        # A mock test is better for this.
        blocked_clause = "This is some text that might be sensitive or harmful if it were actually harmful."
        blocked_category = "Other"
        print(f"\nTesting potentially blocked prompt for category '{blocked_category}':")
        print(f"Clause: {blocked_clause}")
        summary_blocked = service.generate_summary(blocked_clause, blocked_category)
        if summary_blocked:
            print(f"\nGemini Summary (Blocked Test): {summary_blocked}")
        else:
            print("\nFailed to get summary for potentially blocked prompt, or it was indeed blocked (or returned None).")
    else:
        print("GeminiLLMService not fully configured (API Key likely missing or model load failed). Skipping live API test calls in __main__.")
