# src/privacy_interpreter.py
"""
Defines the PrivacyInterpreter for processing privacy policies.
"""

import spacy
from typing import List, Dict, Any
# Attempting to import from sibling directory `privacy_framework`
# This might require adjustments to PYTHONPATH or how the project is structured if run as a script directly
try:
    from .privacy_framework.policy import PrivacyPolicy, DataCategory, Purpose
except ImportError:
    # Fallback for direct execution or different project structures
    from privacy_framework.policy import PrivacyPolicy, DataCategory, Purpose


class PrivacyInterpreter:
    """
    Interprets privacy policy text to extract structured information.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initializes the PrivacyInterpreter.

        Args:
            model_name (str): The name of the spaCy language model to use.
        """
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"spaCy model '{model_name}' not found. "
                  f"Please download it by running: python -m spacy download {model_name}")
            # As a fallback, try loading without the model if it's just for basic structure
            # Or raise an error if the model is strictly necessary for all operations
            self.nlp = None # Or raise specific error/handle appropriately

    def ingest_policy_text(self, policy_text: str) -> str:
        """
        Ingests a plain text privacy policy.

        Args:
            policy_text (str): The raw text of the privacy policy.

        Returns:
            str: The ingested policy text (currently, no transformation is done).
        """
        # In a real scenario, this might involve more complex loading,
        # e.g., from a file path or URL, or handling different encodings.
        return policy_text

    def preprocess_text(self, text: str) -> Any: # spaCy Doc object
        """
        Preprocesses the policy text using spaCy.

        Args:
            text (str): The policy text to preprocess.

        Returns:
            spacy.tokens.Doc: The processed spaCy Doc object.
        """
        if not self.nlp:
            raise EnvironmentError("spaCy NLP model not loaded. Cannot preprocess text.")

        # Basic preprocessing steps might include:
        # - Lowercasing (though often not recommended for NER with some models)
        # - Removing excessive whitespace
        # - Section splitting (more advanced)

        doc = self.nlp(text)
        return doc

    def extract_entities_v1(self, doc: Any) -> Dict[str, List[Any]]: # spaCy Doc object
        """
        Performs a very basic rule-based/keyword-based extraction of potential entities.
        This is a placeholder for more sophisticated NLP techniques.

        Args:
            doc (spacy.tokens.Doc): The processed spaCy Doc object.

        Returns:
            Dict[str, List[Any]]: A dictionary with extracted information.
                                  e.g., {"data_categories": [...], "purposes": [...]}
        """
        extracted_info = {
            "data_categories": [],
            "purposes": [],
            "third_parties": [], # Placeholder
            "retention_keywords": [] # Placeholder for terms related to retention
        }

        # Very naive keyword spotting for demonstration
        # In a real system, this would use NER, dependency parsing, semantic similarity, etc.

        # Potential Data Categories (example keywords)
        data_category_keywords = {
            DataCategory.PERSONAL_INFO: ["name", "email", "address", "phone number", "personal information"],
            DataCategory.LOCATION_DATA: ["location", "gps", "geolocation"],
            DataCategory.USAGE_DATA: ["usage data", "browsing history", "activity"],
            DataCategory.DEVICE_INFO: ["ip address", "device id", "cookie"],
        }

        # Potential Purposes (example keywords)
        purpose_keywords = {
            Purpose.SERVICE_DELIVERY: ["provide our services", "deliver services", "service delivery", "service"],
            Purpose.ANALYTICS: ["analytics", "understand usage", "improve our service"],
            Purpose.MARKETING: ["marketing", "promotional emails", "advertisements"],
        }

        for token in doc:
            # Check for data categories
            for category, keywords in data_category_keywords.items():
                if token.lemma_.lower() in keywords and category not in extracted_info["data_categories"]:
                    extracted_info["data_categories"].append(category)

            # Check for purposes
            for purpose, keywords in purpose_keywords.items():
                if token.lemma_.lower() in keywords and purpose not in extracted_info["purposes"]:
                    extracted_info["purposes"].append(purpose)

        # Example of using NER if entities are labeled (e.g., ORG for third parties)
        for ent in doc.ents:
            if ent.label_ == "ORG": # Assuming ORG entities could be third parties
                if ent.text not in extracted_info["third_parties"]:
                    extracted_info["third_parties"].append(ent.text)
            # Add more entity types as needed

        return extracted_info

    def interpret_policy(self, policy_text: str) -> Dict[str, List[Any]]:
        """
        Main method to ingest, preprocess, and extract information from policy text.

        Args:
            policy_text (str): The raw text of the privacy policy.

        Returns:
            Dict[str, List[Any]]: A dictionary of extracted information.
        """
        ingested_text = self.ingest_policy_text(policy_text)
        doc = self.preprocess_text(ingested_text)
        extracted_data = self.extract_entities_v1(doc)

        # This is a simplified output. Ideally, it would map to a PrivacyPolicy object.
        # For now, returning the raw extraction.
        return extracted_data

if __name__ == '__main__':
    # Example Usage (requires privacy_framework to be in PYTHONPATH or installed)
    interpreter = PrivacyInterpreter()

    sample_policy = """
    Welcome to our service. We collect your name, email, and IP address to provide our services.
    Your location data might be used for analytics. We share your data with Analytics Corp for understanding usage.
    We also use your personal information for marketing purposes if you agree.
    """

    if interpreter.nlp: # Proceed only if model loaded
        print(f"--- Sample Policy Text ---\n{sample_policy}\n")

        processed_doc = interpreter.preprocess_text(sample_policy)
        print(f"--- Processed Doc (first 50 chars) ---\n{processed_doc.text[:50]}...\n")

        extracted_info = interpreter.interpret_policy(sample_policy)
        print("--- Extracted Information (V1) ---")
        for key, value in extracted_info.items():
            if value: # Print only if there's something extracted
                print(f"{key.replace('_', ' ').title()}:")
                for item in value:
                    if isinstance(item, (DataCategory, Purpose)):
                        print(f"  - {item.name} ({item.value})")
                    else:
                        print(f"  - {item}")
        print("\nNote: This is a very basic extraction based on keywords and simple NER.")
    else:
        print("Skipping example usage as spaCy model was not loaded.")
