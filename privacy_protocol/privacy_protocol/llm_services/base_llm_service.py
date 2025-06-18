from abc import ABC, abstractmethod
from typing import List, Tuple, Optional # For type hints

class LLMService(ABC):
    """
    Abstract Base Class for a generic LLM service provider.
    Defines the interface that specific provider clients (e.g., Gemini, OpenAI)
    must implement for plain language summarization.
    """

    @abstractmethod
    def get_api_key_env_var(self) -> str:
        """
        Returns the name of the environment variable that should hold the API key
        for this specific LLM service.
        """
        pass

    @abstractmethod
    def is_api_key_available(self) -> tuple[bool, str | None]:
        """
        Checks if the API key for this service is available in the environment.
        Should be called in the concrete class's __init__ to set up the service.
        Returns a tuple: (is_available: bool, api_key: str | None).
        """
        pass

    @abstractmethod
    def generate_summary(
        self,
        clause_text: str,
        ai_category: str,
    ) -> str | None:
        """
        Generates a plain language summary for a given policy clause text and its AI category.
        Concrete implementations will use their internally configured API key and client.

        Args:
            clause_text: The text of the privacy policy clause.
            ai_category: The AI-determined category of the clause (for context in the prompt).

        Returns:
            A string containing the plain language summary, or None if an error occurs
            or a summary cannot be generated. Specific error messages that are informative
            for the user (e.g., content blocked by safety settings) might also be returned
            as strings by the concrete implementation.
        """
        pass

    @abstractmethod
    def classify_clause(self, clause_text: str, available_categories: List[str]) -> Optional[str]:
        """
        Classifies a given policy clause text into one of the available categories.

        Args:
            clause_text: The text of the privacy policy clause.
            available_categories: A list of valid category strings for the LLM to choose from.

        Returns:
            A string representing one of the `available_categories` that best fits
            the clause_text, or None if classification fails or no suitable category
            is found. The implementing service might also return a default category
            like 'Other' if it's part of `available_categories` and seems appropriate.
        """
        pass

# Example of how a concrete class might use it (for thought, not part of this file):
# import os
# class SomeLLMService(LLMService):
#     API_KEY_ENV_VARIABLE = "SOME_PROVIDER_API_KEY"

#     def __init__(self):
#         self.api_key_is_present, self.api_key = self.is_api_key_available()
#         if self.api_key_is_present:
#             # Configure specific client using self.api_key, e.g., self.client = some_sdk.configure(self.api_key)
#             print(f"SomeLLMService initialized with API key.")
#         else:
#             print(f"Warning: SomeLLMService API key ({self.API_KEY_ENV_VARIABLE}) not found.")


#     def get_api_key_env_var(self) -> str:
#         return self.API_KEY_ENV_VARIABLE

#     def is_api_key_available(self) -> tuple[bool, str | None]:
#         key = os.environ.get(self.get_api_key_env_var())
#         return (True, key) if key else (False, None)

#     def generate_summary(self, clause_text: str, ai_category: str) -> str | None:
#         if not self.api_key_is_present:
#             # Or could return a specific "Service not configured" message
#             return f"Service not configured: API key {self.API_KEY_ENV_VARIABLE} is missing."
#
#         if not clause_text or not clause_text.strip():
#             return "The provided clause text was empty." # Standardized message for this case
#
#         # ... implementation using self.api_key and self.client ...
#         # Example: summary = self.client.summarize(clause_text, context=ai_category)
#         # Handle API errors, safety blocks, etc.
#         return f"Summary from SomeLLMService for '{clause_text[:30]}...' (Category: {ai_category})"
