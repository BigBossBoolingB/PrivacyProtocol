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

    def classify_clause(self, clause_text: str, available_categories: list[str]) -> str | None:
        if not self.api_key_is_present or not self.model:
            # print("Error: GeminiLLMService not configured. Cannot classify clause.")
            # Return None if service not ready, let caller decide on 'Other'
            return None

        if not clause_text or not clause_text.strip():
            # print("Warning: Clause text is empty. Cannot classify.")
            return None # Or 'Other' if 'Other' in available_categories and desired behavior

        try:
            # Ensure 'Other' is an option if it's a fallback for the LLM too.
            # For this prompt, we want the LLM to strictly choose from the list.
            category_list_str = ", ".join([f"'{cat}'" for cat in available_categories]) # Enclose in quotes for LLM
            prompt = (
                f"Your task is to classify the following privacy policy clause into exactly one of the following categories. "
                f"Respond with only the chosen category name from this list, and nothing else. "
                f"Do not add any explanatory text before or after the category name.\n\n"
                f"Available Categories: {category_list_str}\n\n"
                f"Privacy Policy Clause to Classify:\n"
                f"\"{clause_text}\"\n\n"
                f"Category:"
            )

            generation_config = genai.types.GenerationConfig(
                candidate_count=1,
                temperature=0.1 # Lower temperature for more deterministic classification
            )

            response = self.model.generate_content(prompt, generation_config=generation_config)

            if response.parts:
                raw_response_text = ""
                if hasattr(response, 'text') and response.text:
                    raw_response_text = response.text.strip()
                elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    raw_response_text = response.candidates[0].content.parts[0].text.strip()

                if raw_response_text:
                    # Attempt to find an exact match (case-insensitive) from available_categories
                    for cat in available_categories:
                        # Remove potential quotes from LLM output if it echoes like "'Category Name'"
                        cleaned_response = raw_response_text.strip("'\"")
                        if cleaned_response.lower() == cat.lower():
                            return cat # Return the exact category string from our list

                    print(f"Gemini classification response ('{raw_response_text}') not an exact match in available_categories. Trying substring search.")
                    # Fallback: try substring matching if exact failed (less precise)
                    for cat in available_categories:
                        if cat.lower() in raw_response_text.lower():
                            print(f"Found substring match: '{cat}' in '{raw_response_text}'")
                            return cat

                    print(f"Gemini classification response ('{raw_response_text}') did not map to any available category.")
                    return None # Or 'Other' if that's a desired fallback for unmappable responses

            if response.prompt_feedback and response.prompt_feedback.block_reason:
                print(f"Warning: Prompt blocked by Gemini API for classification due to: {response.prompt_feedback.block_reason}")
                return None # Or specific error string like "Classification failed due to safety settings"

            print("Warning: Gemini API returned no content parts for classification.")
            return None

        except google_exceptions.GoogleAPIError as e:
            print(f"Error calling Gemini API for classification: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during Gemini classification: {e}")
            return None


if __name__ == '__main__':
    print("GeminiLLMService Direct Test Script")

    service = GeminiLLMService()


    # Example for __main__ testing of classify_clause
    if service.api_key_is_present and service.model:
        print("\n--- Testing classify_clause ---")
        test_categories = ["Data Collection", "Data Sharing", "Other"]
        clauses_to_test = [
            ("We collect your name and email.", "Data Collection"),
            ("Information is shared with partners.", "Data Sharing"),
            ("This is a neutral statement.", "Other")
        ]
        for clause, expected_cat in clauses_to_test:
            print(f"\nClassifying clause: \"{clause}\"")
            predicted_cat = service.classify_clause(clause, test_categories)
            print(f"  Expected: {expected_cat}, Got: {predicted_cat}")
            if predicted_cat != expected_cat:
                print(f"  Classification MISMATCH for: {clause}")
    else:
        print("GeminiLLMService not fully configured (API Key likely missing or model load failed). Skipping live API test calls in __main__.")
