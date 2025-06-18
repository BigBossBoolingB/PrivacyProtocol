import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import shutil
import re

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import app
from privacy_protocol.interpreter import PrivacyInterpreter
from privacy_protocol.plain_language_translator import PlainLanguageTranslator # For re-init
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
    PROVIDER_ANTHROPIC
)

GEMINI_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.generate_summary'
OPENAI_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.openai_api_client.OpenAILLMService.generate_summary'
ANTHROPIC_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.anthropic_api_client.AnthropicLLMService.generate_summary'

GEMINI_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.is_api_key_available'
OPENAI_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.openai_api_client.OpenAILLMService.is_api_key_available'
ANTHROPIC_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.anthropic_api_client.AnthropicLLMService.is_api_key_available'


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

        # Re-initialize interpreter for each test. This also re-initializes PlainLanguageTranslator,
        # which will call get_llm_service() allowing env var patches to take effect.
        with patch('sys.stdout', new_callable=MagicMock): # Suppress all init prints
            app.interpreter = PrivacyInterpreter()

        keywords_path = os.path.join(os.path.dirname(app.root_path), 'data', 'keywords.json')
        if os.path.exists(keywords_path):
             app.interpreter.load_keywords_from_path(keywords_path)
        else:
             print(f"WARNING (test_app.py setUp): Keywords file not found at {keywords_path} for app.interpreter.", file=sys.stderr)

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
        if ACTIVE_LLM_PROVIDER_ENV_VAR in os.environ:
            del os.environ[ACTIVE_LLM_PROVIDER_ENV_VAR]

    def _get_current_preferences_from_file(self):
        if os.path.exists(CURRENT_PREFERENCES_PATH):
            with open(CURRENT_PREFERENCES_PATH, 'r') as f:
                try: return json.load(f)
                except json.JSONDecodeError: return None
        return None

    def test_main_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Privacy Policy Analyzer", response.data)

    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None))
    def test_analyze_page_empty_input(self, mock_gemini_key_check, mock_gemini_summary_gen):
        # Re-initialize interpreter after @patch.dict to ensure factory picks up env var
        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter = PrivacyInterpreter()
            # Need to reload keywords and prefs for the new interpreter instance
            keywords_path = os.path.join(os.path.dirname(app.root_path), 'data', 'keywords.json')
            if os.path.exists(keywords_path): app.interpreter.load_keywords_from_path(keywords_path)
            app.interpreter.load_user_preferences(get_default_preferences().copy())

        response = self.client.post('/analyze', data={'policy_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No analysis results to display.", response.data)
        mock_gemini_summary_gen.assert_not_called()

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available for this test.")
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(True, 'fake_gemini_key'))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_page_with_gemini_provider_mocked_summary(self, mock_gemini_summary_gen, mock_gemini_key_check):
        expected_summary = "Mocked Gemini Summary for display."
        mock_gemini_summary_gen.return_value = expected_summary

        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter = PrivacyInterpreter()
            keywords_path = os.path.join(os.path.dirname(app.root_path), 'data', 'keywords.json')
            if os.path.exists(keywords_path): app.interpreter.load_keywords_from_path(keywords_path)
            app.interpreter.load_user_preferences(get_default_preferences().copy())

        current_prefs = get_default_preferences()
        current_prefs['data_sharing_for_ads_allowed'] = False
        app.interpreter.load_user_preferences(current_prefs)

        policy_text = "We share your data with third-party advertising partners."
        response = self.client.post('/analyze', data={'policy_text': policy_text})
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes(expected_summary, 'utf-8'), response.data)
        mock_gemini_summary_gen.assert_called()
        self.assertIn(f'<p class="plain-summary"><strong>Plain Language Summary:</strong> {expected_summary}</p>'.encode('utf-8'), response.data)

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available for this test.")
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_OPENAI}, clear=True)
    @patch(OPENAI_SERVICE_KEY_CHECK_PATH, return_value=(True, 'fake_openai_key'))
    @patch(OPENAI_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_page_with_openai_provider_mocked_summary(self, mock_openai_summary_gen, mock_openai_key_check):
        expected_summary = "Mocked OpenAI Summary for display."
        mock_openai_summary_gen.return_value = expected_summary

        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter = PrivacyInterpreter()
            keywords_path = os.path.join(os.path.dirname(app.root_path), 'data', 'keywords.json')
            if os.path.exists(keywords_path): app.interpreter.load_keywords_from_path(keywords_path)
            app.interpreter.load_user_preferences(get_default_preferences().copy())

        current_prefs = get_default_preferences()
        current_prefs['cookies_for_tracking_allowed'] = False
        app.interpreter.load_user_preferences(current_prefs)

        policy_text = "This policy uses cookies for tracking."
        response = self.client.post('/analyze', data={'policy_text': policy_text})
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes(expected_summary, 'utf-8'), response.data)
        mock_openai_summary_gen.assert_called()
        self.assertIn(f'<p class="plain-summary"><strong>Plain Language Summary:</strong> {expected_summary}</p>'.encode('utf-8'), response.data)

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available for this test.")
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_ANTHROPIC}, clear=True)
    @patch(ANTHROPIC_SERVICE_KEY_CHECK_PATH, return_value=(True, 'fake_anthropic_key'))
    @patch(ANTHROPIC_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_page_with_anthropic_provider_mocked_summary(self, mock_anthropic_summary_gen, mock_anthropic_key_check):
        expected_summary = "Mocked Anthropic Summary for display via app."
        mock_anthropic_summary_gen.return_value = expected_summary

        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter = PrivacyInterpreter()
            keywords_path = os.path.join(os.path.dirname(app.root_path), 'data', 'keywords.json')
            if os.path.exists(keywords_path): app.interpreter.load_keywords_from_path(keywords_path)
            app.interpreter.load_user_preferences(get_default_preferences().copy())

        policy_text = "This policy is about data usage patterns with Anthropic."
        app.interpreter.load_user_preferences(get_default_preferences())

        response = self.client.post('/analyze', data={'policy_text': policy_text})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Analysis Results", response.data)
        self.assertIn(bytes(expected_summary, 'utf-8'), response.data)
        mock_anthropic_summary_gen.assert_called_once()
        self.assertIn(f'<p class="plain-summary"><strong>Plain Language Summary:</strong> {expected_summary}</p>'.encode('utf-8'), response.data)


    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available for this test.")
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_page_llm_key_unavailable_uses_fallback_summary(self, mock_gemini_summary_gen, mock_gemini_key_check):
        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter = PrivacyInterpreter()
            keywords_path = os.path.join(os.path.dirname(app.root_path), 'data', 'keywords.json')
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
