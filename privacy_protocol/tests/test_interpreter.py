import unittest
import json
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.interpreter import PrivacyInterpreter
from privacy_protocol.user_preferences import get_default_preferences # For default prefs in tests

# Constants for risk calculation tests - should mirror interpreter.py
AI_CATEGORY_BASE_POINTS = {
    'Data Selling': 20, 'Data Sharing': 15, 'Cookies and Tracking Technologies': 10,
    'Childrens Privacy': 15, 'Data Collection': 10, 'Security': 0,
    'Data Retention': 5, 'Policy Change': 5, 'User Rights': 10,
    'International Data Transfer': 5, 'Contact Information': 0,
    'Consent/Opt-out': 10, 'Other': 1
}
USER_CONCERN_BONUS_POINTS = {
    'High': 15, 'Medium': 7, 'Low': 2, 'None': 0
}
_max_ai_base = 0
for val in AI_CATEGORY_BASE_POINTS.values():
    if val > _max_ai_base:
        _max_ai_base = val
MAX_RISK_POINTS_PER_SENTENCE = _max_ai_base + USER_CONCERN_BONUS_POINTS['High']


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
        # Load default preferences for tests
        self.default_prefs = get_default_preferences()
        self.interpreter.load_user_preferences(self.default_prefs.copy()) # Pass a copy


    def tearDown(self):
        if os.path.exists(self.temp_keywords_file):
            os.remove(self.temp_keywords_file)

    # --- Tests for calculate_risk_assessment ---
    def test_calculate_risk_assessment_empty_input(self):
        assessment = self.interpreter.calculate_risk_assessment([])
        self.assertEqual(assessment['overall_risk_score'], 0)
        self.assertEqual(assessment['service_risk_score'], 0)
        self.assertEqual(assessment['high_concern_count'], 0)
        self.assertEqual(assessment['medium_concern_count'], 0)
        self.assertEqual(assessment['low_concern_count'], 0)
        self.assertEqual(assessment['none_concern_count'], 0)
        self.assertEqual(assessment['num_clauses_analyzed'], 0)

    def test_calculate_risk_assessment_mixed_concerns(self):
        analyzed_data = [
            {'user_concern_level': 'High', 'ai_category': 'Data Selling', 'clause_text': 'Sentence 1'},
            {'user_concern_level': 'High', 'ai_category': 'Cookies and Tracking Technologies', 'clause_text': 'Sentence 2'},
            {'user_concern_level': 'Medium', 'ai_category': 'Data Sharing', 'clause_text': 'Sentence 3'},
            {'user_concern_level': 'Low', 'ai_category': 'Data Collection', 'clause_text': 'Sentence 4'},
            {'user_concern_level': 'None', 'ai_category': 'Other', 'clause_text': 'Sentence 5'},
            {'user_concern_level': 'Medium', 'ai_category': 'Policy Change', 'clause_text': 'Sentence 6'}
        ]
        assessment = self.interpreter.calculate_risk_assessment(analyzed_data)

        # Old score assertion
        self.assertEqual(assessment['overall_risk_score'], 31) # (2*10) + (2*5) + (1*1)
        self.assertEqual(assessment['high_concern_count'], 2)
        self.assertEqual(assessment['medium_concern_count'], 2)
        self.assertEqual(assessment['low_concern_count'], 1)
        self.assertEqual(assessment['none_concern_count'], 1)
        self.assertEqual(assessment['num_clauses_analyzed'], 6)

        # New service_risk_score assertion
        expected_accumulated = (AI_CATEGORY_BASE_POINTS['Data Selling'] + USER_CONCERN_BONUS_POINTS['High']) + \
                               (AI_CATEGORY_BASE_POINTS['Cookies and Tracking Technologies'] + USER_CONCERN_BONUS_POINTS['High']) + \
                               (AI_CATEGORY_BASE_POINTS['Data Sharing'] + USER_CONCERN_BONUS_POINTS['Medium']) + \
                               (AI_CATEGORY_BASE_POINTS['Data Collection'] + USER_CONCERN_BONUS_POINTS['Low']) + \
                               (AI_CATEGORY_BASE_POINTS['Other'] + USER_CONCERN_BONUS_POINTS['None']) + \
                               (AI_CATEGORY_BASE_POINTS['Policy Change'] + USER_CONCERN_BONUS_POINTS['Medium'])
        expected_max_possible = 6 * MAX_RISK_POINTS_PER_SENTENCE
        expected_service_score = round((expected_accumulated / expected_max_possible) * 100) if expected_max_possible else 0
        self.assertEqual(assessment['service_risk_score'], expected_service_score)


    def test_calculate_risk_assessment_only_low_concerns(self):
        analyzed_data = [
            {'user_concern_level': 'Low', 'ai_category': 'User Rights', 'clause_text': 'Sentence 1'},
            {'user_concern_level': 'Low', 'ai_category': 'Contact Information', 'clause_text': 'Sentence 2'}
        ]
        assessment = self.interpreter.calculate_risk_assessment(analyzed_data)
        self.assertEqual(assessment['overall_risk_score'], 2) # 2 * 1
        self.assertEqual(assessment['high_concern_count'], 0)
        self.assertEqual(assessment['medium_concern_count'], 0)
        self.assertEqual(assessment['low_concern_count'], 2)
        self.assertEqual(assessment['none_concern_count'], 0)
        self.assertEqual(assessment['num_clauses_analyzed'], 2)

        expected_accumulated = (AI_CATEGORY_BASE_POINTS['User Rights'] + USER_CONCERN_BONUS_POINTS['Low']) + \
                               (AI_CATEGORY_BASE_POINTS['Contact Information'] + USER_CONCERN_BONUS_POINTS['Low'])
        expected_max_possible = 2 * MAX_RISK_POINTS_PER_SENTENCE
        expected_service_score = round((expected_accumulated / expected_max_possible) * 100) if expected_max_possible else 0
        self.assertEqual(assessment['service_risk_score'], expected_service_score)


    def test_calculate_risk_assessment_with_missing_concern_key(self):
        # Assumes 'user_concern_level' defaults to 'None' and 'ai_category' defaults to 'Other' if missing
        analyzed_data = [
            {'clause_text': 'Sentence 1', 'ai_category': 'Data Collection'}, # Missing user_concern_level
            {'clause_text': 'Sentence 2', 'user_concern_level': 'Low'}     # Missing ai_category
        ]
        assessment = self.interpreter.calculate_risk_assessment(analyzed_data)
        self.assertEqual(assessment['overall_risk_score'], 1) # 0 for first (None), 1 for second (Low)
        self.assertEqual(assessment['none_concern_count'], 1)
        self.assertEqual(assessment['low_concern_count'], 1)
        self.assertEqual(assessment['num_clauses_analyzed'], 2)

        expected_accumulated = (AI_CATEGORY_BASE_POINTS['Data Collection'] + USER_CONCERN_BONUS_POINTS['None']) + \
                               (AI_CATEGORY_BASE_POINTS['Other'] + USER_CONCERN_BONUS_POINTS['Low'])
        expected_max_possible = 2 * MAX_RISK_POINTS_PER_SENTENCE
        expected_service_score = round((expected_accumulated / expected_max_possible) * 100) if expected_max_possible else 0
        self.assertEqual(assessment['service_risk_score'], expected_service_score)

    # --- NLP Dependent Tests ---
    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_structure_and_ai_category(self):
        text = "We collect your email for marketing."
        results = self.interpreter.analyze_text(text)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        sentence_result = results[0]
        self.assertIn("clause_text", sentence_result)
        self.assertEqual(sentence_result["clause_text"], text)
        self.assertIn("ai_category", sentence_result)
        self.assertEqual(sentence_result["ai_category"], "Data Collection")
        self.assertIn("keyword_matches", sentence_result)
        self.assertIsInstance(sentence_result["keyword_matches"], list)
        self.assertIn("plain_language_summary", sentence_result)
        self.assertIsInstance(sentence_result["plain_language_summary"], str)
        self.assertEqual(sentence_result["plain_language_summary"],
                         self.interpreter.plain_language_translator.dummy_explanations.get("Data Collection"))
        self.assertIn("user_concern_level", sentence_result)
        self.assertEqual(sentence_result["user_concern_level"], "Low")

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_with_one_keyword_match(self):
        text = "We share your information with third-party vendors."
        # Default prefs: data_sharing_for_ads_allowed = False -> High concern for "Data Sharing" AI category
        self.interpreter.load_user_preferences(self.default_prefs.copy()) # Ensure fresh default
        self.interpreter.user_preferences['data_sharing_for_ads_allowed'] = False

        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        sentence_result = results[0]
        self.assertEqual(sentence_result["clause_text"], text)
        self.assertEqual(sentence_result["ai_category"], "Data Sharing")
        self.assertEqual(len(sentence_result["keyword_matches"]), 1)
        keyword_match = sentence_result["keyword_matches"][0]
        self.assertEqual(keyword_match["keyword"], "third-party")
        self.assertEqual(keyword_match["explanation"], "Test explanation for third-party.")
        self.assertEqual(keyword_match["category"], "Data Sharing")
        self.assertEqual(sentence_result["plain_language_summary"],
                         self.interpreter.plain_language_translator.dummy_explanations.get("Data Sharing"))
        self.assertIn("user_concern_level", sentence_result)
        self.assertEqual(sentence_result["user_concern_level"], "High")

        # Test with data_sharing_for_ads_allowed = True
        self.interpreter.user_preferences['data_sharing_for_ads_allowed'] = True
        results_ads_allowed = self.interpreter.analyze_text(text)
        self.assertEqual(results_ads_allowed[0]["user_concern_level"], "Low")

        self.interpreter.load_user_preferences(self.default_prefs.copy()) # Reset

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_with_multiple_keywords_in_same_sentence(self):
        text = "Our policy on data selling and user tracking is clear."
        self.interpreter.load_user_preferences(self.default_prefs.copy()) # Ensure fresh default (data_selling_allowed=False)
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        sentence_result = results[0]
        self.assertEqual(sentence_result["clause_text"], text)
        self.assertEqual(sentence_result["ai_category"], "Data Selling")
        self.assertEqual(len(sentence_result["keyword_matches"]), 2)
        self.assertIn("user_concern_level", sentence_result)
        self.assertEqual(sentence_result["user_concern_level"], "High")

        found_keywords = sorted([km["keyword"] for km in sentence_result["keyword_matches"]])
        self.assertListEqual(found_keywords, ["data selling", "tracking"])

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_multiple_sentences_varied_matches_and_concerns(self):
        text = "We collect data for analytics. We do not sell data. We use tracking for ads."

        # Ensure preferences are set for this multi-part test
        current_prefs = self.default_prefs.copy()
        current_prefs['data_selling_allowed'] = False
        current_prefs['cookies_for_tracking_allowed'] = False # This will make "tracking for ads" High concern
        current_prefs['data_sharing_for_ads_allowed'] = False # For later, if "tracking for ads" implies sharing
        self.interpreter.load_user_preferences(current_prefs)

        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 3)

        # Sentence 1: "We collect data for analytics."
        s1 = results[0]
        self.assertEqual(s1["clause_text"], "We collect data for analytics.")
        self.assertEqual(s1["ai_category"], "Data Collection")
        self.assertEqual(len(s1["keyword_matches"]), 0)
        self.assertEqual(s1["plain_language_summary"], self.interpreter.plain_language_translator.dummy_explanations.get("Data Collection"))
        self.assertEqual(s1["user_concern_level"], "Low")

        # Sentence 2: "We do not sell data."
        s2 = results[1]
        self.assertEqual(s2["clause_text"], "We do not sell data.")
        self.assertEqual(s2["ai_category"], "Data Selling")
        self.assertEqual(len(s2["keyword_matches"]), 0)
        self.assertEqual(s2["plain_language_summary"], self.interpreter.plain_language_translator.dummy_explanations.get("Data Selling"))
        self.assertEqual(s2["user_concern_level"], "High") # Due to data_selling_allowed = False

        # Sentence 3: "We use tracking for ads."
        s3 = results[2]
        self.assertEqual(s3["clause_text"], "We use tracking for ads.")
        self.assertEqual(s3["ai_category"], "Cookies and Tracking Technologies")
        self.assertEqual(len(s3["keyword_matches"]), 1)
        self.assertEqual(s3["keyword_matches"][0]["keyword"], "tracking")
        self.assertEqual(s3["plain_language_summary"], self.interpreter.plain_language_translator.dummy_explanations.get("Cookies and Tracking Technologies"))
        self.assertEqual(s3["user_concern_level"], "High") # Due to cookies_for_tracking_allowed = False

        self.interpreter.load_user_preferences(self.default_prefs.copy()) # Reset

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_keyword_case_insensitivity(self):
        text = "This policy mentions Third-Party services."
        self.interpreter.load_user_preferences(self.default_prefs.copy())
        self.interpreter.user_preferences['data_sharing_for_ads_allowed'] = False # Makes Data Sharing High concern

        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        sentence_result = results[0]
        self.assertEqual(sentence_result["clause_text"], text)
        self.assertEqual(sentence_result["ai_category"], "Data Sharing")
        self.assertEqual(len(sentence_result["keyword_matches"]), 1)
        self.assertEqual(sentence_result["keyword_matches"][0]["keyword"], "third-party")
        self.assertEqual(sentence_result["user_concern_level"], "High")
        self.interpreter.load_user_preferences(self.default_prefs.copy())


    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_empty_string_after_strip_no_results(self):
        text = "     .     "
        results = self.interpreter.analyze_text(text)
        if results:
            self.assertEqual(len(results), 1)
            sentence_result = results[0]
            self.assertEqual(sentence_result['clause_text'], ".")
            self.assertEqual(sentence_result['ai_category'], 'Other')
            self.assertEqual(len(sentence_result['keyword_matches']), 0)
            self.assertEqual(sentence_result['user_concern_level'], "None") # 'Other' and no keywords = 'None'
        else:
            self.assertEqual(len(results), 0)


    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_negation_direct_not_no_keyword_match(self):
        text = "We do not share third-party data."
        self.interpreter.load_user_preferences(self.default_prefs.copy())
        self.interpreter.user_preferences['data_sharing_for_ads_allowed'] = False

        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        sentence_result = results[0]
        self.assertEqual(sentence_result["clause_text"], text)
        self.assertEqual(sentence_result["ai_category"], "Data Sharing")
        self.assertEqual(len(sentence_result["keyword_matches"]), 0)
        self.assertEqual(sentence_result["user_concern_level"], "High") # AI cat is still Data Sharing, pref makes it High
        self.interpreter.load_user_preferences(self.default_prefs.copy())

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_negation_direct_no_no_keyword_match(self):
        text = "There is no data selling."
        self.interpreter.load_user_preferences(self.default_prefs.copy()) # data_selling_allowed = False by default

        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        sentence_result = results[0]
        self.assertEqual(sentence_result["clause_text"], text)
        self.assertEqual(sentence_result["ai_category"], "Data Selling")
        self.assertEqual(len(sentence_result["keyword_matches"]), 0)
        self.assertEqual(sentence_result["user_concern_level"], "High") # AI cat + pref

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_keyword_not_negated_is_matched(self):
        text = "We may use third-party services."
        self.interpreter.load_user_preferences(self.default_prefs.copy())
        self.interpreter.user_preferences['data_sharing_for_ads_allowed'] = False # To make it High

        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        sentence_result = results[0]
        self.assertEqual(sentence_result["clause_text"], text)
        self.assertEqual(sentence_result["ai_category"], "Data Sharing")
        self.assertEqual(len(sentence_result["keyword_matches"]), 1)
        self.assertEqual(sentence_result["keyword_matches"][0]["keyword"], "third-party")
        self.assertEqual(sentence_result["user_concern_level"], "High")
        self.interpreter.load_user_preferences(self.default_prefs.copy())

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available")
    def test_analyze_text_no_keywords_in_text_but_ai_categories(self):
        text = "We collect your information for our records. This is important for us."
        self.interpreter.load_user_preferences(self.default_prefs.copy())
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 2)

        s1 = results[0]
        self.assertEqual(s1['clause_text'], "We collect your information for our records.")
        self.assertEqual(s1['ai_category'], "Data Collection")
        self.assertEqual(len(s1['keyword_matches']), 0)
        self.assertEqual(s1['user_concern_level'], "Low")

        s2 = results[1]
        self.assertEqual(s2['clause_text'], "This is important for us.")
        self.assertEqual(s2['ai_category'], "Other")
        self.assertEqual(len(s2['keyword_matches']), 0)
        self.assertEqual(s2['user_concern_level'], "None")


    # --- NLP Independent Tests (or tests that should behave gracefully if NLP is absent) ---
    def test_keyword_loading(self):
        self.assertTrue(len(self.interpreter.keywords_data) > 0, "Keywords should be loaded.")
        self.assertIn("third-party", self.interpreter.keywords_data)

    def test_analyze_text_empty_text_input_no_results(self):
        results = self.interpreter.analyze_text("")
        self.assertEqual(len(results), 0)

    def test_analyze_text_none_input_no_results(self):
        results = self.interpreter.analyze_text(None)
        self.assertEqual(len(results), 0)

    def test_analyze_text_integer_input_no_results(self):
        results = self.interpreter.analyze_text(123)
        self.assertEqual(len(results), 0)

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available.")
    def test_keyword_missing_explanation_or_category_in_matches(self):
        original_keywords_data = self.interpreter.keywords_data
        self.interpreter.keywords_data = {
            "new_keyword_test": {}
        }
        self.interpreter.load_user_preferences(self.default_prefs.copy()) # Ensure prefs

        text = "This policy has a new_keyword_test."
        results = self.interpreter.analyze_text(text)

        self.interpreter.keywords_data = original_keywords_data

        self.assertEqual(len(results), 1)
        sentence_result = results[0]
        self.assertEqual(sentence_result['clause_text'], text)
        self.assertEqual(sentence_result['ai_category'], "Other") # No AI rule for "new_keyword_test"

        self.assertEqual(len(sentence_result['keyword_matches']), 1)
        keyword_match = sentence_result['keyword_matches'][0]
        self.assertEqual(keyword_match["keyword"], "new_keyword_test")
        self.assertEqual(keyword_match["explanation"], "No explanation available.")
        self.assertEqual(keyword_match["category"], "Uncategorized")
        self.assertEqual(sentence_result['user_concern_level'], "Low") # Has keyword, but no specific pref rule triggers High/Medium for 'Other' AI cat / 'Uncategorized' keyword cat


    def test_loading_nonexistent_keywords_file_returns_empty_results(self):
        temp_interpreter = PrivacyInterpreter()
        temp_interpreter.load_keywords_from_path("nonexistent_keywords.json")
        temp_interpreter.load_user_preferences(self.default_prefs.copy()) # Load prefs for temp interpreter
        self.assertEqual(temp_interpreter.keywords_data, {})

        results = temp_interpreter.analyze_text("Some text with potential keywords.")
        if temp_interpreter.nlp:
            for sentence_result in results:
                self.assertEqual(len(sentence_result["keyword_matches"]), 0)
                # AI cat could be something, concern would be Low or None
        else:
            self.assertEqual(len(results), 0)

    def test_loading_corrupted_keywords_file_returns_empty_results(self):
        corrupted_file = "corrupted_keywords_test.json"
        with open(corrupted_file, 'w') as f:
            f.write("this is not valid json {")

        temp_interpreter = PrivacyInterpreter()
        temp_interpreter.load_keywords_from_path(corrupted_file)
        temp_interpreter.load_user_preferences(self.default_prefs.copy())

        if os.path.exists(corrupted_file):
            os.remove(corrupted_file)

        self.assertEqual(temp_interpreter.keywords_data, {})
        results = temp_interpreter.analyze_text("Some text.")
        if temp_interpreter.nlp:
            for sentence_result in results:
                self.assertEqual(len(sentence_result["keyword_matches"]), 0)
        else:
            self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
