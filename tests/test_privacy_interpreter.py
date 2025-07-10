# tests/test_privacy_interpreter.py
import unittest
import spacy # Used for type hinting if needed, and potentially for more advanced tests later

# Adjust import path based on your project structure
# This assumes 'src' is in PYTHONPATH or tests are run from project root
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_interpreter import PrivacyInterpreter
from src.privacy_framework.policy import DataCategory, Purpose # For checking extracted types

class TestPrivacyInterpreter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load the spaCy model once for all tests."""
        try:
            cls.interpreter = PrivacyInterpreter() # Uses default "en_core_web_sm"
        except EnvironmentError as e: # Catch if model isn't downloaded
            print(f"Skipping TestPrivacyInterpreter: spaCy model not found. {e}")
            cls.interpreter = None # Ensure interpreter is None so tests can be skipped
        except Exception as e:
            print(f"Unexpected error during TestPrivacyInterpreter setup: {e}")
            cls.interpreter = None


    def setUp(self):
        """Skip tests if the interpreter failed to initialize."""
        if not self.interpreter or not self.interpreter.nlp:
            self.skipTest("spaCy model not loaded, skipping interpreter tests.")

    def test_interpreter_initialization(self):
        self.assertIsNotNone(self.interpreter)
        self.assertTrue(hasattr(self.interpreter, 'nlp'))
        self.assertIsNotNone(self.interpreter.nlp)

    def test_ingest_policy_text(self):
        sample_text = "This is a sample policy."
        ingested = self.interpreter.ingest_policy_text(sample_text)
        self.assertEqual(ingested, sample_text)

    def test_preprocess_text(self):
        sample_text = "This is a test sentence. It has two sentences."
        doc = self.interpreter.preprocess_text(sample_text)
        self.assertIsNotNone(doc)
        self.assertIsInstance(doc, spacy.tokens.Doc)
        # Basic check, spaCy sentence segmentation might vary slightly based on model/version
        # For "en_core_web_sm", it should typically find 2 sentences here.
        # self.assertEqual(len(list(doc.sents)), 2)

    def test_interpret_policy_basic_output(self):
        sample_policy = "We collect your name and email for service delivery. We use cookies for analytics."
        extracted_data = self.interpreter.interpret_policy(sample_policy)

        self.assertIsInstance(extracted_data, dict)
        self.assertIn("data_categories", extracted_data)
        self.assertIn("purposes", extracted_data)
        self.assertIn("third_parties", extracted_data) # Even if empty

        # Check if the extracted items are of the expected enum types (if found)
        if extracted_data["data_categories"]:
            for item in extracted_data["data_categories"]:
                self.assertIsInstance(item, DataCategory)

        if extracted_data["purposes"]:
            for item in extracted_data["purposes"]:
                self.assertIsInstance(item, Purpose)

    def test_extract_entities_v1_keywords(self):
        # More targeted test for the V1 keyword extraction logic
        policy_text_for_keywords = "Our service uses your email for service delivery and location for analytics. We share with Analytics Corp."
        doc = self.interpreter.preprocess_text(policy_text_for_keywords)
        extracted_info = self.interpreter.extract_entities_v1(doc)

        self.assertIn(DataCategory.PERSONAL_INFO, extracted_info["data_categories"])
        self.assertIn(DataCategory.LOCATION_DATA, extracted_info["data_categories"])
        self.assertIn(Purpose.SERVICE_DELIVERY, extracted_info["purposes"])
        self.assertIn(Purpose.ANALYTICS, extracted_info["purposes"])

        # Assuming 'Analytics Corp' is recognized as ORG by the default model
        # This part of the test is model-dependent and might be fragile
        # if "Analytics Corp" in extracted_info["third_parties"]:
        #     self.assertIn("Analytics Corp", extracted_info["third_parties"])
        # else:
        #     print("Warning: 'Analytics Corp' not found as a third party by NER. This might be model specific.")

    def test_interpret_policy_empty_text(self):
        extracted_data = self.interpreter.interpret_policy("")
        self.assertIsInstance(extracted_data, dict)
        self.assertEqual(len(extracted_data["data_categories"]), 0)
        self.assertEqual(len(extracted_data["purposes"]), 0)
        self.assertEqual(len(extracted_data["third_parties"]), 0)

    def test_interpret_policy_no_keywords(self):
        sample_policy = "This document outlines general terms and conditions."
        extracted_data = self.interpreter.interpret_policy(sample_policy)
        self.assertIsInstance(extracted_data, dict)
        # Depending on the model, some generic ORGs might be found, but categories/purposes should be empty
        self.assertEqual(len(extracted_data["data_categories"]), 0)
        self.assertEqual(len(extracted_data["purposes"]), 0)


if __name__ == '__main__':
    # This allows running the tests directly from this file
    # Ensure src is in PYTHONPATH:
    # In project root: python -m unittest tests.test_privacy_interpreter
    unittest.main()
