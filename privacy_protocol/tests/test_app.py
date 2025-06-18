import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import shutil
import re
import time # For diff testing

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import app
from privacy_protocol.interpreter import PrivacyInterpreter
from privacy_protocol.plain_language_translator import PlainLanguageTranslator
from privacy_protocol.user_preferences import (
    get_default_preferences,
    CURRENT_PREFERENCES_PATH,
    DEFAULT_PREFERENCES_PATH,
    USER_DATA_DIR,
)
from privacy_protocol.llm_services import (
    llm_service_factory,
    ACTIVE_LLM_PROVIDER_ENV_VAR,
    PROVIDER_GEMINI,
    PROVIDER_OPENAI,
    PROVIDER_ANTHROPIC,
    PROVIDER_AZURE_OPENAI
)
# Import from policy_history_manager
from privacy_protocol.policy_history_manager import (
    save_policy_analysis as save_policy_direct, # Alias to avoid conflict if app also imports it
    generate_policy_identifier as generate_id_direct,
    list_analyzed_policies as list_policies_direct,
    get_policy_analysis as get_policy_direct,
    POLICY_HISTORY_DIR # For cleanup
)


GEMINI_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.generate_summary'
OPENAI_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.openai_api_client.OpenAILLMService.generate_summary'
ANTHROPIC_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.anthropic_api_client.AnthropicLLMService.generate_summary'
AZURE_OPENAI_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.azure_openai_client.AzureOpenAILLMService.generate_summary'

GEMINI_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.is_api_key_available'
OPENAI_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.openai_api_client.OpenAILLMService.is_api_key_available'
ANTHROPIC_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.anthropic_api_client.AnthropicLLMService.is_api_key_available'
AZURE_OPENAI_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.azure_openai_client.AzureOpenAILLMService.is_api_key_available'


SPACY_MODEL_AVAILABLE = False
NLP_UNAVAILABLE_MESSAGE_IN_RESULTS = "NLP model 'en_core_web_sm' was not loaded"
try:
    import spacy
    spacy.load("en_core_web_sm")
    SPACY_MODEL_AVAILABLE = True
except (ImportError, OSError):
    pass


class TestWebApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter = PrivacyInterpreter()

        # Keywords path relative to app.py's location (which is project_root/privacy_protocol/)
        keywords_path = os.path.join(app.root_path, 'data', 'keywords.json')
        if os.path.exists(keywords_path):
             app.interpreter.load_keywords_from_path(keywords_path)
        # else:
             # print(f"WARNING (test_app.py setUp): Keywords file not found at {keywords_path} for app.interpreter.", file=sys.stderr)

        # User preferences directory
        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)
        os.makedirs(USER_DATA_DIR)
        default_prefs_content = get_default_preferences()
        with open(DEFAULT_PREFERENCES_PATH, 'w') as f:
            json.dump(default_prefs_content, f)
        if os.path.exists(CURRENT_PREFERENCES_PATH):
            os.remove(CURRENT_PREFERENCES_PATH)
        app.interpreter.load_user_preferences(default_prefs_content.copy())

        # Policy history directory
        if os.path.exists(POLICY_HISTORY_DIR):
            shutil.rmtree(POLICY_HISTORY_DIR)
        os.makedirs(POLICY_HISTORY_DIR, exist_ok=True)


    def tearDown(self):
        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)
        if os.path.exists(POLICY_HISTORY_DIR):
            shutil.rmtree(POLICY_HISTORY_DIR)
        if ACTIVE_LLM_PROVIDER_ENV_VAR in os.environ:
            del os.environ[ACTIVE_LLM_PROVIDER_ENV_VAR]

    def _get_current_preferences_from_file(self):
        if os.path.exists(CURRENT_PREFERENCES_PATH):
            with open(CURRENT_PREFERENCES_PATH, 'r') as f:
                try: return json.load(f)
                except json.JSONDecodeError: return None
        return None

    def _create_dummy_historical_analysis(self, suffix=""):
        # Helper to create a file that list_analyzed_policies and get_policy_analysis can find
        identifier = generate_id_direct() + suffix # Ensure some uniqueness if called rapidly
        data = {
            'policy_identifier': identifier,
            'source_url': f'http://example.com/policy{suffix}',
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'full_policy_text': f"Historical policy text {suffix}.",
            'analysis_results': [{'clause_text': f"Historical Clause {suffix}", 'ai_category': 'Other', 'recommendations':[], 'user_concern_level':'None', 'plain_language_summary':''}],
            'risk_assessment': {'overall_risk_score': 1, 'high_concern_count':0, 'medium_concern_count':0, 'low_concern_count':1, 'none_concern_count':0}
        }
        save_policy_direct(
            identifier, data['full_policy_text'], data['analysis_results'],
            data['risk_assessment'], data['source_url']
        )
        return identifier, data


    def test_main_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Privacy Policy Analyzer", response.data)

    # --- /analyze route tests with history and diffing ---
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None)) # No API key for Gemini
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH) # Mock the method
    def test_analyze_first_policy_saves_and_shows_no_history_message(self, mock_gemini_summary_gen, mock_gemini_key_check):
        with patch('sys.stdout', new_callable=MagicMock): app.interpreter = PrivacyInterpreter()
        app.interpreter.load_keywords_from_path(os.path.join(app.root_path, 'data', 'keywords.json'))
        app.interpreter.load_user_preferences(get_default_preferences().copy())

        policy_text = "This is the very first policy."
        response = self.client.post('/analyze', data={'policy_text': policy_text})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No previous analysis found in history to compare against.", response.data)

        # Check if saved
        saved_policies = list_policies_direct()
        self.assertEqual(len(saved_policies), 1)
        self.assertEqual(saved_policies[0]['source_url'], "Pasted Text Input") # Default source for direct analysis

    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_same_policy_shows_no_changes_message(self, mock_gemini_summary_gen, mock_gemini_key_check):
        policy_text = "This policy will be analyzed twice."
        # First analysis (saves it)
        with patch('sys.stdout', new_callable=MagicMock): app.interpreter = PrivacyInterpreter()
        app.interpreter.load_keywords_from_path(os.path.join(app.root_path, 'data', 'keywords.json'))
        app.interpreter.load_user_preferences(get_default_preferences().copy())
        self.client.post('/analyze', data={'policy_text': policy_text})

        # Second analysis of the exact same text
        with patch('sys.stdout', new_callable=MagicMock): app.interpreter = PrivacyInterpreter() # Re-init for clean state if needed
        app.interpreter.load_keywords_from_path(os.path.join(app.root_path, 'data', 'keywords.json'))
        app.interpreter.load_user_preferences(get_default_preferences().copy())
        response = self.client.post('/analyze', data={'policy_text': policy_text})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No textual changes detected compared to the most recent analysis in history.", response.data)

    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_different_policy_shows_diff_table(self, mock_gemini_summary_gen, mock_gemini_key_check):
        original_text = "Version 1 of the policy."
        updated_text = "Version 2 of the policy, with changes."

        with patch('sys.stdout', new_callable=MagicMock): app.interpreter = PrivacyInterpreter()
        app.interpreter.load_keywords_from_path(os.path.join(app.root_path, 'data', 'keywords.json'))
        app.interpreter.load_user_preferences(get_default_preferences().copy())
        self.client.post('/analyze', data={'policy_text': original_text}) # Save V1

        with patch('sys.stdout', new_callable=MagicMock): app.interpreter = PrivacyInterpreter()
        app.interpreter.load_keywords_from_path(os.path.join(app.root_path, 'data', 'keywords.json'))
        app.interpreter.load_user_preferences(get_default_preferences().copy())
        response = self.client.post('/analyze', data={'policy_text': updated_text}) # Analyze V2
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Changes Since Last Analysis", response.data)
        self.assertIn(b'<table class="diff"', response.data) # difflib specific
        self.assertIn(b'class="diff_sub"', response.data) # Removed "Version 1"
        self.assertIn(b'class="diff_add"', response.data) # Added "Version 2"

    # --- /history and /history/view routes ---
    def test_history_list_page_empty(self):
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No policy analyses found in history.", response.data)

    def test_history_list_page_with_items(self):
        id1, data1 = self._create_dummy_historical_analysis("item1")
        time.sleep(0.001) # ensure different timestamp if generating another
        id2, data2 = self._create_dummy_historical_analysis("item2")

        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes(id1, 'utf-8'), response.data)
        self.assertIn(bytes(data1['source_url'], 'utf-8'), response.data)
        self.assertIn(bytes(id2, 'utf-8'), response.data)
        self.assertIn(bytes(data2['source_url'], 'utf-8'), response.data)
        self.assertIn(b'View Details', response.data)

    def test_view_historical_analysis_found(self):
        identifier, data = self._create_dummy_historical_analysis("view_found")
        response = self.client.get(f'/history/view/{identifier}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Stored Analysis:", response.data)
        self.assertIn(bytes(data['full_policy_text'], 'utf-8'), response.data)
        self.assertIn(bytes(data['analysis_results'][0]['clause_text'], 'utf-8'), response.data)
        self.assertIn(bytes(str(data['risk_assessment']['overall_risk_score']), 'utf-8'), response.data)
        self.assertIn(b"Back to History List", response.data)

    def test_view_historical_analysis_not_found(self):
        response = self.client.get('/history/view/non_existent_id_xyz', follow_redirects=True)
        self.assertEqual(response.status_code, 200) # After redirect to history list
        self.assertIn(b"Could not find stored analysis with ID: non_existent_id_xyz", response.data)
        self.assertIn(b"Analysis History", response.data) # Should be on history list page

    # ... (Keep existing tests for /preferences, and other /analyze aspects like provider mocking) ...
    # The following are existing tests, slightly adapted if needed for clarity or consistency.
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_page_llm_key_unavailable_uses_fallback_summary(self, mock_gemini_summary_gen, mock_gemini_key_check):
        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter = PrivacyInterpreter()
            keywords_path = os.path.join(app.root_path, 'data', 'keywords.json')
            if os.path.exists(keywords_path): app.interpreter.load_keywords_from_path(keywords_path)
            app.interpreter.load_user_preferences(get_default_preferences().copy())

        policy_text = "We collect your email."
        app.interpreter.load_user_preferences(get_default_preferences())

        response = self.client.post('/analyze', data={'policy_text': policy_text})
        self.assertEqual(response.status_code, 200)

        expected_dummy_summary = app.interpreter.plain_language_translator.dummy_explanations.get("Data Collection")
        self.assertIn(bytes(expected_dummy_summary, 'utf-8'), response.data)
        mock_gemini_summary_gen.assert_not_called()

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
