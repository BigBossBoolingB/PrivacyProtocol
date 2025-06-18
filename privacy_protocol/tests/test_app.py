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
from privacy_protocol.user_preferences import (
    get_default_preferences,
    CURRENT_PREFERENCES_PATH,
    DEFAULT_PREFERENCES_PATH,
    USER_DATA_DIR,
)
from privacy_protocol.llm_services import llm_service_factory, ACTIVE_LLM_PROVIDER_ENV_VAR, PROVIDER_GEMINI, PROVIDER_OPENAI
from privacy_protocol.llm_services.gemini_api_client import GeminiLLMService
from privacy_protocol.llm_services.openai_api_client import OpenAILLMService

# Paths for mocking specific service methods that are part of the INSTANCE, not the factory.
# The factory will return a REAL instance (Gemini or OpenAI), then we mock methods ON that instance.
# This is different from mocking the constructor as done in test_llm_service_factory.

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

        # Ensure the PlainLanguageTranslator's LLM service is re-initialized based on current env for each test
        # Suppress prints during this re-initialization for cleaner test logs
        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter.plain_language_translator.llm_service = llm_service_factory.get_llm_service()
            app.interpreter.plain_language_translator.load_model() # Re-run load_model to reflect new service

    def tearDown(self):
        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)
        if ACTIVE_LLM_PROVIDER_ENV_VAR in os.environ: # Clean up env var if tests set it
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

    @patch('privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.generate_summary')
    @patch('privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.is_api_key_available', return_value=(False, None))
    def test_analyze_page_empty_input(self, mock_gemini_key_check, mock_gemini_summary_gen):
        with patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True):
             # Re-initialize translator's service with current env var for this test
            with patch('sys.stdout', new_callable=MagicMock):
                app.interpreter.plain_language_translator.llm_service = llm_service_factory.get_llm_service()
                app.interpreter.plain_language_translator.load_model()

            response = self.client.post('/analyze', data={'policy_text': ''})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"No analysis results to display.", response.data)
            mock_gemini_summary_gen.assert_not_called()

    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available for this test.")
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch('privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.is_api_key_available', return_value=(True, 'fake_gemini_key'))
    @patch('privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.generate_summary')
    def test_analyze_page_with_gemini_provider_mocked_summary(self, mock_gemini_summary_gen, mock_gemini_key_check):
        expected_summary = "Mocked Gemini Summary for display."
        mock_gemini_summary_gen.return_value = expected_summary

        with patch('sys.stdout', new_callable=MagicMock): # Suppress re-init prints
            app.interpreter.plain_language_translator.llm_service = llm_service_factory.get_llm_service()
            app.interpreter.plain_language_translator.load_model()

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
    @patch('privacy_protocol.llm_services.openai_api_client.OpenAILLMService.is_api_key_available', return_value=(True, 'fake_openai_key'))
    @patch('privacy_protocol.llm_services.openai_api_client.OpenAILLMService.generate_summary')
    def test_analyze_page_with_openai_provider_mocked_summary(self, mock_openai_summary_gen, mock_openai_key_check):
        expected_summary = "Mocked OpenAI Summary for display."
        mock_openai_summary_gen.return_value = expected_summary

        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter.plain_language_translator.llm_service = llm_service_factory.get_llm_service()
            app.interpreter.plain_language_translator.load_model()

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
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch('privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.is_api_key_available', return_value=(False, None))
    @patch('privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.generate_summary')
    def test_analyze_page_llm_key_unavailable_uses_fallback_summary(self, mock_gemini_summary_gen, mock_gemini_key_check):
        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter.plain_language_translator.llm_service = llm_service_factory.get_llm_service()
            app.interpreter.plain_language_translator.load_model()

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
