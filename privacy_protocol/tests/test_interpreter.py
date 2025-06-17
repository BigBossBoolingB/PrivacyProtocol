import unittest
import json
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.interpreter import PrivacyInterpreter

# Attempt to load spaCy and the model once to determine if NLP-dependent tests can run
SPACY_MODEL_AVAILABLE = False
try:
    import spacy
    spacy.load("en_core_web_sm") # Try to load model to check availability
    SPACY_MODEL_AVAILABLE = True
except ImportError:
    print("Skipping NLP tests: spaCy library not installed.", file=sys.stderr)
except OSError:
    print("Skipping NLP tests: spaCy model 'en_core_web_sm' not found. Run 'python -m spacy download en_core_web_sm'", file=sys.stderr)


class TestPrivacyInterpreter(unittest.TestCase):

    def setUp(self):
        self.keywords_data = {
            "third-party": {
                "explanation": "Test explanation for third-party.",
                "category": "Data Sharing"
            },
            "data selling": {
                "explanation": "Test explanation for data selling.",
                "category": "Data Selling"
            },
            "tracking": {
                "explanation": "Test explanation for tracking.",
                "category": "User Activity Monitoring"
            }
        }
        self.temp_keywords_file = "temp_keywords_interpreter_test.json"
        with open(self.temp_keywords_file, 'w') as f:
            json.dump(self.keywords_data, f)

        self.interpreter = PrivacyInterpreter()
        self.interpreter.load_keywords_from_path(self.temp_keywords_file)


    def tearDown(self):
        if os.path.exists(self.temp_keywords_file):
            os.remove(self.temp_keywords_file)

    # --- NLP Dependent Tests ---
    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_with_one_keyword_and_clause(self):
        text = "This is a first sentence. We may share your information with a third-party. This is a third sentence."
        expected_clause = "We may share your information with a third-party."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1, f"Results: {results}")
        self.assertEqual(results[0]["keyword"], "third-party")
        self.assertEqual(results[0]["clause_text"], expected_clause)

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_with_multiple_keywords_in_different_clauses(self):
        text = "Our policy on data selling is clear in this sentence. User tracking is discussed in the next one."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 2)
        keywords_found = {item['keyword']: item['clause_text'] for item in results}
        self.assertEqual(keywords_found.get("data selling"), "Our policy on data selling is clear in this sentence.")
        self.assertEqual(keywords_found.get("tracking"), "User tracking is discussed in the next one.")

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_with_multiple_keywords_in_same_clause(self):
        text = "This single sentence mentions both data selling and user tracking."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 2)
        keywords_in_results = [r['keyword'] for r in results]
        self.assertIn('data selling', keywords_in_results)
        self.assertIn('tracking', keywords_in_results)
        for item in results:
            self.assertEqual(item['clause_text'], "This single sentence mentions both data selling and user tracking.")

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_keyword_case_insensitivity_with_clause(self):
        text = "This policy mentions Third-Party services in one sentence. And another sentence."
        expected_clause = "This policy mentions Third-Party services in one sentence."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["keyword"], "third-party")
        self.assertEqual(results[0]["clause_text"], expected_clause)

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_empty_string_after_strip(self):
        text = "     .     "
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 0)

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_negation_direct_not(self):
        text = "We do not share third-party data."
        results = self.interpreter.analyze_text(text)
        # "third-party" should be negated by "not"
        found_third_party = any(item['keyword'] == 'third-party' for item in results)
        self.assertFalse(found_third_party, "Keyword 'third-party' should be negated by 'not'.")

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_negation_direct_no(self):
        text = "There is no data selling."
        results = self.interpreter.analyze_text(text)
        found_data_selling = any(item['keyword'] == 'data selling' for item in results)
        self.assertFalse(found_data_selling, "Keyword 'data selling' should be negated by 'no'.")

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_negation_contracted_dont(self):
        text = "We don't allow tracking of users."
        results = self.interpreter.analyze_text(text)
        found_tracking = any(item['keyword'] == 'tracking' for item in results)
        self.assertFalse(found_tracking, "Keyword 'tracking' should be negated by 'don't'.")

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_keyword_not_negated(self):
        text = "We may use third-party services."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["keyword"], "third-party")

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_negation_further_away_should_still_flag(self):
        # Current basic negation looks at words immediately before.
        # "We are not evil people. We engage in data selling." - "data selling" should be flagged.
        text = "We are not evil people. We engage in data selling."
        results = self.interpreter.analyze_text(text)
        found_data_selling = any(item['keyword'] == 'data selling' for item in results)
        self.assertTrue(found_data_selling, "Keyword 'data selling' should be flagged as negation is not immediately preceding.")
        if found_data_selling:
            for item in results:
                if item['keyword'] == 'data selling':
                    self.assertEqual(item['clause_text'], "We engage in data selling.")


    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_multiple_keywords_one_negated(self):
        # "We do not sell data, but we use tracking for analytics."
        # "data selling" should be negated. "tracking" should be flagged.
        text = "We do not sell data, but we use tracking for analytics."
        results = self.interpreter.analyze_text(text)

        found_data_selling = any(item['keyword'] == 'data selling' for item in results)
        self.assertFalse(found_data_selling, "Keyword 'data selling' should be negated.")

        found_tracking = any(item['keyword'] == 'tracking' for item in results)
        self.assertTrue(found_tracking, "Keyword 'tracking' should be flagged.")
        if found_tracking:
            for item in results:
                if item['keyword'] == 'tracking':
                    # The clause is the whole sentence as per current spaCy sentence segmentation
                    self.assertEqual(item['clause_text'], "We do not sell data, but we use tracking for analytics.")


    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_negation_at_start_of_sentence_no(self):
        text = "No data selling is permitted."
        results = self.interpreter.analyze_text(text)
        found_data_selling = any(item['keyword'] == 'data selling' for item in results)
        self.assertFalse(found_data_selling, "Keyword 'data selling' should be negated by 'No' at sentence start.")

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_negation_word_part_of_another_word(self):
        # E.g. "notebook" should not trigger negation for "book" if "book" was a keyword.
        # Using "third-party" and "noteworthy"
        text = "This is a noteworthy third-party service."
        results = self.interpreter.analyze_text(text)
        found_third_party = any(item['keyword'] == 'third-party' for item in results)
        self.assertTrue(found_third_party, "'third-party' should be flagged as 'noteworthy' is not a negation of it.")
        if found_third_party:
             for item in results:
                if item['keyword'] == 'third-party':
                    self.assertEqual(item['clause_text'], "This is a noteworthy third-party service.")

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_keyword_following_negation_of_different_concept(self):
        text = "We are not evil, and we use tracking."
        results = self.interpreter.analyze_text(text)
        found_tracking = any(item['keyword'] == 'tracking' for item in results)
        self.assertTrue(found_tracking, "Keyword 'tracking' should be flagged as 'not' applies to 'evil'.")


    # --- NLP Independent Tests (or tests that should behave gracefully if NLP is absent) ---
    def test_keyword_loading(self):
        self.assertTrue(len(self.interpreter.keywords_data) > 0, "Keywords should be loaded.")
        self.assertIn("third-party", self.interpreter.keywords_data)

    def test_analyze_text_no_keywords_in_text(self):
        text = "This policy is clean and respects user privacy."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 0)

    def test_analyze_text_empty_text_input(self):
        results = self.interpreter.analyze_text("")
        self.assertEqual(len(results), 0)

    def test_analyze_text_none_input(self):
        results = self.interpreter.analyze_text(None)
        self.assertEqual(len(results), 0)

    def test_analyze_text_integer_input(self):
        results = self.interpreter.analyze_text(123)
        self.assertEqual(len(results), 0)

    def test_keyword_missing_explanation_or_category(self):
        keywords_missing_data = {"new_keyword": {}}

        temp_interpreter = PrivacyInterpreter()

        if not temp_interpreter.nlp:
            self.skipTest("spaCy model 'en_core_web_sm' not available for test_keyword_missing_explanation_or_category's analyze_text part.")

        specific_temp_keywords_file = "temp_missing_keywords.json"
        with open(specific_temp_keywords_file, 'w') as f:
            json.dump(keywords_missing_data, f)
        temp_interpreter.load_keywords_from_path(specific_temp_keywords_file)

        text = "This policy has a new_keyword."
        results = temp_interpreter.analyze_text(text)

        if os.path.exists(specific_temp_keywords_file):
            os.remove(specific_temp_keywords_file)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["keyword"], "new_keyword")
        self.assertEqual(results[0]["explanation"], "No explanation available.")
        self.assertEqual(results[0]["category"], "Uncategorized")
        self.assertEqual(results[0]["clause_text"], text)


    def test_loading_nonexistent_keywords_file(self):
        temp_interpreter = PrivacyInterpreter()
        temp_interpreter.load_keywords_from_path("nonexistent_keywords.json")
        self.assertEqual(temp_interpreter.keywords_data, {})
        results = temp_interpreter.analyze_text("Some text.")
        self.assertEqual(len(results), 0)

    def test_loading_corrupted_keywords_file(self):
        corrupted_file = "corrupted_keywords.json"
        with open(corrupted_file, 'w') as f:
            f.write("this is not valid json {")

        temp_interpreter = PrivacyInterpreter()
        temp_interpreter.load_keywords_from_path(corrupted_file)

        if os.path.exists(corrupted_file):
            os.remove(corrupted_file)

        self.assertEqual(temp_interpreter.keywords_data, {})
        results = temp_interpreter.analyze_text("Some text.")
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
