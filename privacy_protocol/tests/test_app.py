import unittest
import os
import sys
import json
import shutil
import re

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import app
from privacy_protocol.user_preferences import (
    get_default_preferences,
    CURRENT_PREFERENCES_PATH,
    DEFAULT_PREFERENCES_PATH,
    USER_DATA_DIR,
)

# Determine if spaCy model is available
SPACY_MODEL_AVAILABLE = False
NLP_UNAVAILABLE_MESSAGE_IN_RESULTS = "NLP model 'en_core_web_sm' was not loaded"
try:
    import spacy
    spacy.load("en_core_web_sm")
    SPACY_MODEL_AVAILABLE = True
    print("test_app.py: spaCy model 'en_core_web_sm' IS available.", file=sys.stderr)
except ImportError:
    print("test_app.py: spaCy library not installed. Some web tests will be skipped.", file=sys.stderr)
except OSError:
    print("test_app.py: spaCy model 'en_core_web_sm' not found. Some web tests will be skipped.", file=sys.stderr)


class TestWebApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        if not app.interpreter.keywords_data:
             print("WARNING (test_app.py setUp): Keywords not loaded in app.interpreter.", file=sys.stderr)

        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)
        os.makedirs(USER_DATA_DIR)
        default_prefs_content = get_default_preferences()
        with open(DEFAULT_PREFERENCES_PATH, 'w') as f:
            json.dump(default_prefs_content, f)
        if os.path.exists(CURRENT_PREFERENCES_PATH):
            os.remove(CURRENT_PREFERENCES_PATH)
        app.interpreter.load_user_preferences(default_prefs_content.copy())


    def tearDown(self):
        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)

    def _get_current_preferences_from_file(self):
        if os.path.exists(CURRENT_PREFERENCES_PATH):
            with open(CURRENT_PREFERENCES_PATH, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return None
        return None

    def test_main_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Privacy Policy Analyzer", response.data)
        self.assertIn(b"Paste Privacy Policy Text:", response.data)

    def test_analyze_page_empty_input(self):
        response = self.client.post('/analyze', data={'policy_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No analysis results to display.", response.data)
        self.assertIn(b"No text submitted.", response.data)
        # Risk assessment should show 0 for empty input
        self.assertIn(b"<h3>Overall Privacy Risk Assessment</h3>", response.data)
        self.assertIn(b"<strong>Overall Risk Score:</strong> <span class=\"risk-score-value\">0</span>", response.data)
        self.assertIn(b"<strong>High Concern Clauses:</strong> 0", response.data)


    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available for this test.")
    def test_analyze_page_with_data_and_nlp_model(self):
        current_prefs = get_default_preferences()
        current_prefs['data_sharing_for_ads_allowed'] = False # Trigger High concern for Data Sharing AI
        app.interpreter.load_user_preferences(current_prefs)

        sample_text = "We share your data with third-party advertising partners for tracking purposes."
        response = self.client.post('/analyze', data={'policy_text': sample_text})
        self.assertEqual(response.status_code, 200)
        self.assertIn(sample_text.encode(), response.data)
        self.assertIn(b'<div class="sentence-block concern-high">', response.data)
        self.assertIn(b'<p class="ai-category">AI Predicted Category: Data Sharing</p>', response.data)
        expected_summary = app.interpreter.plain_language_translator.dummy_explanations.get("Data Sharing")
        self.assertIn(b'<p class="plain-summary"><strong>Plain Language Summary:</strong> ' + expected_summary.encode() + b'</p>', response.data)
        self.assertIn(b'<p class="concern-level-text"><strong>Concern Level:</strong> High</p>', response.data)
        self.assertIn(b"<strong>Keyword:</strong> third-party", response.data)
        self.assertIn(b"<strong>Keyword:</strong> tracking", response.data)

        # Risk Assessment Checks: 1 sentence, AI "Data Sharing", pref makes it High.
        self.assertIn(b"<h3>Overall Privacy Risk Assessment</h3>", response.data)
        self.assertIn(b"<strong>Overall Risk Score:</strong> <span class=\"risk-score-value\">10</span>", response.data)
        self.assertIn(b"<strong>High Concern Clauses:</strong> 1", response.data)
        self.assertIn(b"<strong>Medium Concern Clauses:</strong> 0", response.data)
        self.assertIn(b"<strong>Low Concern Clauses:</strong> 0", response.data)

        app.interpreter.load_user_preferences(get_default_preferences()) # Reset

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available for this test.")
    def test_analyze_page_with_negated_keyword_and_nlp_model(self):
        current_prefs = get_default_preferences()
        current_prefs['data_selling_allowed'] = False
        app.interpreter.load_user_preferences(current_prefs)

        sample_text = "We do not sell data ever. Our commitment is to your privacy."
        response = self.client.post('/analyze', data={'policy_text': sample_text})
        self.assertEqual(response.status_code, 200)
        self.assertIn(sample_text.encode(), response.data)
        self.assertNotIn(b"<strong>Keyword:</strong> data selling", response.data)
        self.assertIn(b'<div class="sentence-block concern-high">', response.data)
        self.assertIn(b'<p class="ai-category">AI Predicted Category: Data Selling</p>', response.data)
        expected_summary = app.interpreter.plain_language_translator.dummy_explanations.get("Data Selling")
        self.assertIn(b'<p class="plain-summary"><strong>Plain Language Summary:</strong> ' + expected_summary.encode() + b'</p>', response.data)
        self.assertIn(b'<p class="concern-level-text"><strong>Concern Level:</strong> High</p>', response.data)
        self.assertIn(b"<em>No specific keywords flagged in this sentence by the keyword scanner.</em>", response.data)

        # Risk Assessment Checks: 1 sentence, AI "Data Selling", pref makes it High.
        self.assertIn(b"<h3>Overall Privacy Risk Assessment</h3>", response.data)
        self.assertIn(b"<strong>Overall Risk Score:</strong> <span class=\"risk-score-value\">10</span>", response.data)
        self.assertIn(b"<strong>High Concern Clauses:</strong> 1", response.data)

        app.interpreter.load_user_preferences(get_default_preferences())


    @unittest.skipIf(SPACY_MODEL_AVAILABLE, "spaCy model IS available, skipping test for NLP unavailable scenario.")
    def test_analyze_page_no_nlp_model(self):
        sample_text = "This is some policy text with third-party."
        response = self.client.post('/analyze', data={'policy_text': sample_text})
        self.assertEqual(response.status_code, 200)
        self.assertIn(NLP_UNAVAILABLE_MESSAGE_IN_RESULTS.encode(), response.data)
        self.assertIn(b"No analysis results to display.", response.data) # Interpreter returns empty list if no NLP
        # Risk assessment should show 0 if no analysis results
        self.assertIn(b"<strong>Overall Risk Score:</strong> <span class=\"risk-score-value\">0</span>", response.data)


    # --- Tests for /preferences route ---
    def test_preferences_page_get(self):
        response = self.client.get('/preferences')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your Privacy Preferences", response.data)
        select_block_for_selling = response.data.decode('utf-8').split('<select name="data_selling_allowed"')[1].split('</select>')[0]
        self.assertIn('<option value="false" selected', select_block_for_selling)


    def test_preferences_page_post_and_redirect(self):
        new_preference_values = {
            'data_selling_allowed': 'true',
            'data_sharing_for_ads_allowed': 'true',
            'data_sharing_for_analytics_allowed': 'false',
            'cookies_for_tracking_allowed': 'false',
            'policy_changes_notification_required': 'false',
            'childrens_privacy_strict': 'false'
        }
        response = self.client.post('/preferences', data=new_preference_values, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Preferences saved successfully!', response.data)

        saved_prefs = self._get_current_preferences_from_file()
        self.assertIsNotNone(saved_prefs)
        self.assertTrue(saved_prefs['data_selling_allowed'])
        self.assertFalse(saved_prefs['data_sharing_for_analytics_allowed'])

        select_block_for_selling_after_post = response.data.decode('utf-8').split('<select name="data_selling_allowed"')[1].split('</select>')[0]
        self.assertIn('<option value="true" selected', select_block_for_selling_after_post)

        select_block_for_analytics_after_post = response.data.decode('utf-8').split('<select name="data_sharing_for_analytics_allowed"')[1].split('</select>')[0]
        self.assertIn('<option value="false" selected', select_block_for_analytics_after_post)


if __name__ == '__main__':
    unittest.main()
