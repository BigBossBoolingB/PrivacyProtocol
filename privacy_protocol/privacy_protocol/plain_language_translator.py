from .clause_categories import CLAUSE_CATEGORIES
from .llm_services import get_llm_service # Import the factory

class PlainLanguageTranslator:
    def __init__(self):
        self.llm_service = get_llm_service() # Get configured LLM service instance

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
        service_name = type(self.llm_service).__name__ if self.llm_service else 'None configured'
        print(f"PlainLanguageTranslator: Attempting to use LLM service: {service_name}.")
        if self.llm_service and self.llm_service.is_api_key_available()[0]:
            print(f"  LLM Service '{service_name}' API Key is available.")
        else:
            status_detail = "API Key not available or service client init failed." if self.llm_service else "No service configured."
            print(f"  LLM Service '{service_name}' - {status_detail} Will use fallbacks.")


    def translate(self, clause_text: str, ai_category: str) -> str:
        if not isinstance(ai_category, str):
            ai_category = 'Other'

        if not clause_text or not clause_text.strip():
            print("PlainLanguageTranslator: Empty clause text provided, using default summary for category.")
            return self.dummy_explanations.get(ai_category, self.default_summary)

        key_available = self.llm_service.is_api_key_available()[0] if self.llm_service else False
        if not self.llm_service or not key_available:
            # This print can be verbose if called per sentence, consider removing or logging to debug level
            # service_type_name = type(self.llm_service).__name__ if self.llm_service else 'N/A'
            # print(f"LLM Service ({service_type_name}) not available or API key missing, using fallback for '{ai_category}'.")
            return self.dummy_explanations.get(ai_category, self.default_summary)

        # Attempt to get summary from the configured LLM service
        api_summary = self.llm_service.generate_summary(clause_text, ai_category)

        if api_summary is not None and api_summary.strip():
            # LLMService concrete implementations are expected to return:
            # 1. A valid summary string.
            # 2. A specific error message string (e.g., "Could not generate...", "The provided clause text was empty.").
            # 3. None (if a low-level/unexpected error occurred).
            # The client specific error messages like "The provided clause text was empty." or "Could not generate..." are passed through.
            return api_summary
        else:
            # Service returned None or an empty/whitespace string.
            service_type_name = type(self.llm_service).__name__ # Should be safe due to earlier checks
            print(f"LLM service {service_type_name} returned None or empty summary. Falling back for category {ai_category}.")
            return self.dummy_explanations.get(ai_category, self.default_summary)

if __name__ == '__main__':
    # __main__ will now use the factory to get the default LLM (Gemini) or one specified by ENV VAR
    # It will also show whether the respective API key was found.
    print("--- PlainLanguageTranslator (with LLM Service Factory) ---")
    translator = PlainLanguageTranslator() # load_model() is called in __init__

    test_clauses_with_categories = [
        ("We collect your name and email address for account setup.", "Data Collection"),
        ("We may share your information with trusted third-party service providers for analytics only.", "Data Sharing"),
        ("This is a clause with no specific AI category match for dummy fallbacks.", "New Hypothetical Category"),
        ("", "Data Collection"), # Empty clause text test
        ("Another clause about cookies.", "Cookies and Tracking Technologies")
    ]

    print("\n--- Translating Sample Clauses ---")
    for clause, category in test_clauses_with_categories:
        print(f"\nOriginal Clause: '{clause}'")
        print(f"AI Category: {category}")
        summary = translator.translate(clause, category)
        print(f"Plain Summary: {summary}")

    # Example to test a specific provider if needed, by setting ENV VAR before running,
    # or by directly calling get_llm_service with an override (though translator uses default from factory)
    # print("\n--- Testing with specific provider (e.g. OpenAI, if key is set) ---")
    # from privacy_protocol.llm_services import llm_service_factory
    # os.environ[llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR] = llm_service_factory.PROVIDER_OPENAI
    # translator_openai = PlainLanguageTranslator() # Will pick up OpenAI via factory due to ENV VAR
    # print(f"API Key Available for OpenAI Translator: {translator_openai.llm_service.is_api_key_available()[0] if translator_openai.llm_service else False}")
    # summary_openai = translator_openai.translate("We sell your data with consent.", "Data Selling")
    # print(f"OpenAI Summary for 'Data Selling': {summary_openai}")
    # # Clean up env var if set only for test
    # del os.environ[llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR]
