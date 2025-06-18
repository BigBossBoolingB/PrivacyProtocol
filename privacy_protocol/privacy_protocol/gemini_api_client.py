import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions # For more specific error handling

# It's good practice to load .env variables if python-dotenv is used,
# but for this setup, we'll rely on the environment variable being set directly.
# from dotenv import load_dotenv
# load_dotenv() # Call this if you want to use a .env file for local dev

GEMINI_API_KEY_ENV_VAR = "GEMINI_API_KEY"
# Specify the model to use, e.g., 'gemini-pro' or a specific version if needed
# For plain text summarization, 'gemini-pro' is suitable.
# If a vision model or other specific type were needed, this would change.
DEFAULT_GEMINI_MODEL = 'gemini-pro'

def get_gemini_api_key():
    """Retrieves the Gemini API key from environment variables."""
    api_key = os.environ.get(GEMINI_API_KEY_ENV_VAR)
    if not api_key:
        print(f"Warning: Gemini API key not found in environment variable {GEMINI_API_KEY_ENV_VAR}")
    return api_key

def generate_plain_language_summary_with_gemini(api_key: str, clause_text: str, ai_category: str) -> str | None:
    """
    Generates a plain language summary for a policy clause using the Gemini API.

    Args:
        api_key: The Gemini API key.
        clause_text: The text of the privacy policy clause.
        ai_category: The AI-determined category of the clause (for context in the prompt).

    Returns:
        A string containing the plain language summary, or None if an error occurs.
    """
    if not api_key:
        print("Error: Gemini API key is missing. Cannot generate summary.")
        return None
    if not clause_text or not clause_text.strip():
        # print("Warning: Clause text is empty. Cannot generate summary.") # Or return a specific message
        return "The provided clause text was empty."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)

        # Construct a more detailed prompt for better results
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

        # Generation configuration (optional, but can help control output)
        generation_config = genai.types.GenerationConfig(
            candidate_count=1, # Generate only one response
            # temperature=0.7, # Lower for more deterministic, higher for more creative. Default is often fine.
            # max_output_tokens=150 # Limit the length of the summary
        )

        response = model.generate_content(prompt, generation_config=generation_config)

        if response.parts:
            # Assuming the first part contains the text summary
            # Need to check response structure, often it's response.text for simple cases
            # For Gemini, it might be response.candidates[0].content.parts[0].text if using more complex generation
            # Let's assume response.text for simplicity based on typical Gemini direct text generation.
            # If generate_content returns a GenerationResponse object, text is often in response.text
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            # Fallback for more complex candidate structures if the above isn't right
            elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text.strip()
            else:
                print("Warning: Gemini API response structure not as expected or empty.")
                return None
        else:
            # This case handles if the response itself has no parts, indicating an issue or empty generation.
            # Also check for safety ratings if prompt was blocked. response.prompt_feedback can show this.
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                print(f"Warning: Prompt blocked by Gemini API due to: {response.prompt_feedback.block_reason}")
                return f"Could not generate summary due to safety settings (Reason: {response.prompt_feedback.block_reason})."
            print("Warning: Gemini API returned no content parts.")
            return None

    except google_exceptions.GoogleAPIError as e:
        print(f"Error calling Gemini API: {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors during API interaction
        print(f"An unexpected error occurred with Gemini API client: {e}")
        return None

if __name__ == '__main__':
    print("Gemini API Client Script")
    # This block is for basic manual testing if you have the API key set up.
    # It won't run in automated tests without mocking.
    test_api_key = get_gemini_api_key()
    if test_api_key:
        print("API Key found.")
        sample_clause = "We may share your personal information, including your browsing history and purchase records, with our advertising partners to display targeted advertisements to you on other websites."
        sample_category = "Data Sharing"
        print(f"\nTesting summary generation for category '{sample_category}':")
        print(f"Clause: {sample_clause}")
        summary = generate_plain_language_summary_with_gemini(test_api_key, sample_clause, sample_category)
        if summary:
            print(f"\nGemini Summary: {summary}")
        else:
            print("\nFailed to get summary from Gemini.")

        # Test blocked prompt scenario (example, might not actually trigger blocking)
        blocked_clause = "This is some text that might be sensitive or harmful."
        blocked_category = "Other"
        print(f"\nTesting potentially blocked prompt for category '{blocked_category}':")
        print(f"Clause: {blocked_clause}")
        summary_blocked = generate_plain_language_summary_with_gemini(test_api_key, blocked_clause, blocked_category)
        if summary_blocked:
            print(f"\nGemini Summary (Blocked Test): {summary_blocked}")
        else:
            print("\nFailed to get summary for potentially blocked prompt, or it was indeed blocked.")

    else:
        print("API Key not found. Skipping live API test.")
