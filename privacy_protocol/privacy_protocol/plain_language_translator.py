from .clause_categories import CLAUSE_CATEGORIES
from .gemini_api_client import generate_plain_language_summary_with_gemini, get_gemini_api_key

class PlainLanguageTranslator:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        self.api_key_available = True if self.api_key else False

        self.dummy_explanations = {
            'Data Collection': "This section likely describes what personal information the company collects from you and how.",
            'Data Sharing': "This part probably details if and how your information is shared with third parties or other entities.",
            'Data Usage': "This likely explains for what purposes the company uses the information it collects.",
            'User Rights': "This section should outline your rights regarding your personal data, such as access, correction, or deletion.",
            'Security': "This part is expected to describe the security measures the company takes to protect your data.",
            'Data Retention': "This likely covers how long the company keeps your information.",
            'Consent/Opt-out': "This section may explain how your consent is obtained or how you can opt-out of certain data uses or communications.",
            'Policy Change': "This part usually describes how the company will inform you about changes to this privacy policy.",
            'International Data Transfer': "This likely discusses if your data is transferred to other countries and the safeguards for such transfers.",
            'Childrens Privacy': "This section should address the company's policies regarding the collection of data from children.",
            'Contact Information': "This part should provide contact details if you have questions about the policy or your data.",
            'Cookies and Tracking Technologies': "This likely explains the use of cookies, web beacons, and other tracking technologies on their services.",
            'Data Selling': "This section may indicate whether the company sells your personal information to third parties.",
        }
        self.default_summary = "Plain language summary could not be generated at this time."
        self.load_model()

    def load_model(self):
        if self.api_key_available:
            print("PlainLanguageTranslator: Using Gemini API for summaries.")
        else:
            print("PlainLanguageTranslator: Gemini API key not available. Using fallback summaries.")

    def translate(self, clause_text: str, ai_category: str) -> str:
        if not isinstance(ai_category, str):
            ai_category = 'Other'

        if not self.api_key_available:
            # print(f"Debug: Fallback due to no API key. Category: {ai_category}")
            return self.dummy_explanations.get(ai_category, self.default_summary)

        # The gemini_api_client's generate_plain_language_summary_with_gemini already handles empty clause_text
        # and returns a specific message "The provided clause text was empty."
        # So, we call it directly.

        api_summary = generate_plain_language_summary_with_gemini(self.api_key, clause_text, ai_category)

        if api_summary is not None:
            client_error_prefixes_or_exact_matches = [
                "Could not generate summary due to safety settings",
                "The provided clause text was empty.", # Exact match from client for empty clause
                # "Error calling Gemini API" # This would typically result in api_summary being None
                # "Gemini API key is missing" # This would also typically result in api_summary being None
            ]
            is_client_specific_message = False
            if api_summary == "The provided clause text was empty.": # Exact match check
                is_client_specific_message = True
            else: # Prefix checks for others
                for prefix in client_error_prefixes_or_exact_matches:
                    if api_summary.startswith(prefix):
                        is_client_specific_message = True
                        break

            if is_client_specific_message:
                # Pass through specific messages from the client (like "empty text" or "safety settings")
                return api_summary
            elif api_summary.strip(): # Ensure it's not empty string after strip, and not an error handled above
                return api_summary  # Successfully got a usable summary from Gemini
            else:
                # API returned an empty string or something unexpected that wasn't an error but isn't usable
                print(f"Gemini API client returned an empty or unusable summary: '{api_summary}'. Falling back for category {ai_category}.")
        else:
            # API call itself failed (e.g., network, internal API key issue passed to client, etc.), api_summary is None
            print(f"Gemini API call failed (returned None). Falling back for category {ai_category}.")

        # Fallback Logic: Use dummy explanations or default summary
        return self.dummy_explanations.get(ai_category, self.default_summary)

if __name__ == '__main__':
    translator = PlainLanguageTranslator()
    # The load_model print message is now part of __init__ calling load_model
    print(f"API Key Available for Translator: {translator.api_key_available}")

    test_clauses_with_categories = [
        ("We collect your name and email address.", "Data Collection"),
        ("We may share your information with trusted third-party service providers.", "Data Sharing"),
        ("This is a clause with no specific AI category match for dummy fallbacks.", "New Hypothetical Category"),
        ("", "Data Collection") # Empty clause text test
    ]

    print("\n--- PlainLanguageTranslator (potentially with Gemini API) Output ---")
    for clause, category in test_clauses_with_categories:
        print(f"\nOriginal Clause: '{clause}'") # Added quotes for clarity
        print(f"AI Category: {category}")
        summary = translator.translate(clause, category)
        print(f"Plain Summary: {summary}")
