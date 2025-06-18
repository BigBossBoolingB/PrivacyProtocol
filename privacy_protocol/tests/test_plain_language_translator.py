import unittest
from unittest.mock import patch, MagicMock
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.plain_language_translator import PlainLanguageTranslator
from privacy_protocol.clause_categories import CLAUSE_CATEGORIES
from privacy_protocol.llm_services.base_llm_service import LLMService # For spec

# Path for mocking get_llm_service, as used in plain_language_translator.py
GET_LLM_SERVICE_PATH = 'privacy_protocol.plain_language_translator.get_llm_service'

class TestPlainLanguageTranslator(unittest.TestCase):

    @patch(GET_LLM_SERVICE_PATH)
    def test_translate_uses_configured_llm_service_success(self, mock_get_llm_service):
        mock_llm_instance = MagicMock(spec=LLMService)
        mock_llm_instance.is_api_key_available.return_value = (True, 'fake_key_active')
        expected_summary = "Summary from active LLM service."
        mock_llm_instance.generate_summary.return_value = expected_summary
        mock_get_llm_service.return_value = mock_llm_instance

        # Suppress init prints from translator for cleaner test output
        with patch('sys.stdout', new_callable=MagicMock):
            translator = PlainLanguageTranslator()

        clause_text = "Some important clause."
        ai_category = "Data Collection"
        summary = translator.translate(clause_text, ai_category)

        self.assertEqual(summary, expected_summary)
        # is_api_key_available is called in load_model() (via __init__) and again in translate()
        self.assertEqual(mock_llm_instance.is_api_key_available.call_count, 2)
        mock_llm_instance.generate_summary.assert_called_once_with(clause_text, ai_category)
        # Let's be more specific if needed, or ensure load_model is also patched if its prints are an issue.
        # For now, checking the call during translate is key.

    @patch(GET_LLM_SERVICE_PATH)
    def test_translate_llm_service_key_not_available_uses_fallback(self, mock_get_llm_service):
        mock_llm_instance = MagicMock(spec=LLMService)
        # is_api_key_available for the service instance will be called twice:
        # 1. In PlainLanguageTranslator.load_model() (during __init__)
        # 2. In PlainLanguageTranslator.translate()
        mock_llm_instance.is_api_key_available.return_value = (False, None)
        mock_get_llm_service.return_value = mock_llm_instance

        with patch('sys.stdout', new_callable=MagicMock):
            translator = PlainLanguageTranslator()

        ai_category = "Data Sharing"
        dummy_fallback = translator.dummy_explanations.get(ai_category, translator.default_summary)
        summary = translator.translate("Another clause.", ai_category)

        self.assertEqual(summary, dummy_fallback)
        mock_llm_instance.generate_summary.assert_not_called()
        # is_api_key_available would be called in load_model and then in translate
        self.assertEqual(mock_llm_instance.is_api_key_available.call_count, 2)


    @patch(GET_LLM_SERVICE_PATH)
    def test_translate_llm_service_returns_none_uses_fallback(self, mock_get_llm_service):
        mock_llm_instance = MagicMock(spec=LLMService)
        mock_llm_instance.is_api_key_available.return_value = (True, 'fake_key_active')
        mock_llm_instance.generate_summary.return_value = None # Simulate LLM service failure
        mock_get_llm_service.return_value = mock_llm_instance

        with patch('sys.stdout', new_callable=MagicMock):
            translator = PlainLanguageTranslator()

        ai_category = "User Rights"
        dummy_fallback = translator.dummy_explanations.get(ai_category, translator.default_summary)
        summary = translator.translate("A user rights clause.", ai_category)
        self.assertEqual(summary, dummy_fallback)
        mock_llm_instance.generate_summary.assert_called_once_with("A user rights clause.", ai_category)

    @patch(GET_LLM_SERVICE_PATH)
    def test_translate_llm_service_returns_specific_error_message(self, mock_get_llm_service):
        mock_llm_instance = MagicMock(spec=LLMService)
        mock_llm_instance.is_api_key_available.return_value = (True, 'fake_key_active')
        error_message_from_service = "Could not generate summary due to safety settings"
        mock_llm_instance.generate_summary.return_value = error_message_from_service
        mock_get_llm_service.return_value = mock_llm_instance

        with patch('sys.stdout', new_callable=MagicMock):
            translator = PlainLanguageTranslator()

        summary = translator.translate("A problematic clause.", "Data Usage")
        self.assertEqual(summary, error_message_from_service) # Specific error should be passed through

    @patch(GET_LLM_SERVICE_PATH)
    def test_translate_llm_service_returns_empty_string_uses_fallback(self, mock_get_llm_service):
        mock_llm_instance = MagicMock(spec=LLMService)
        mock_llm_instance.is_api_key_available.return_value = (True, 'fake_key_active')
        mock_llm_instance.generate_summary.return_value = "   " # Empty or whitespace
        mock_get_llm_service.return_value = mock_llm_instance

        with patch('sys.stdout', new_callable=MagicMock):
            translator = PlainLanguageTranslator()

        ai_category = "Data Collection"
        dummy_fallback = translator.dummy_explanations.get(ai_category, translator.default_summary)
        summary = translator.translate("Some clause.", ai_category)
        self.assertEqual(summary, dummy_fallback)


    @patch(GET_LLM_SERVICE_PATH)
    def test_translate_empty_clause_text_uses_fallback_directly(self, mock_get_llm_service):
        mock_llm_instance = MagicMock(spec=LLMService)
        mock_llm_instance.is_api_key_available.return_value = (True, 'fake_key_active')
        mock_get_llm_service.return_value = mock_llm_instance

        with patch('sys.stdout', new_callable=MagicMock):
            translator = PlainLanguageTranslator()

        ai_category = "Data Collection"
        # Expected: direct fallback, specific message for empty text from client is NOT used here
        # because PlainLanguageTranslator handles empty clause text before calling the service.
        expected_fallback = translator.dummy_explanations.get(ai_category, translator.default_summary)

        summary_empty = translator.translate("", ai_category)
        self.assertEqual(summary_empty, expected_fallback)

        summary_whitespace = translator.translate("   ", ai_category)
        self.assertEqual(summary_whitespace, expected_fallback)

        mock_llm_instance.generate_summary.assert_not_called() # Service's generate_summary not called

    @patch(GET_LLM_SERVICE_PATH)
    def test_translate_no_llm_service_configured_uses_fallback(self, mock_get_llm_service):
        mock_get_llm_service.return_value = None # Factory returns None

        with patch('sys.stdout', new_callable=MagicMock):
            translator = PlainLanguageTranslator()

        ai_category = "Data Collection"
        expected_fallback = translator.dummy_explanations.get(ai_category, translator.default_summary)
        summary = translator.translate("Some clause.", ai_category)
        self.assertEqual(summary, expected_fallback)

    def test_all_defined_categories_have_fallback_summaries(self):
        # This test ensures that every category in CLAUSE_CATEGORIES gets some fallback response
        # when the LLM service is effectively unavailable (mocked as None).
        with patch(GET_LLM_SERVICE_PATH, return_value=None):
            with patch('sys.stdout', new_callable=MagicMock):
                translator = PlainLanguageTranslator()

            for category in CLAUSE_CATEGORIES:
                summary = translator.translate("Some clause text", category)
                self.assertIsInstance(summary, str)
                if category in translator.dummy_explanations:
                    self.assertEqual(summary, translator.dummy_explanations[category])
                else:
                    self.assertEqual(summary, translator.default_summary)

    def test_translate_none_or_invalid_category_type_fallback(self):
        # If category is None or not a string, it should become 'Other' and then use fallback
        # if LLM service is unavailable or fails for 'Other'.
        with patch(GET_LLM_SERVICE_PATH) as mock_get_llm_service:
            mock_llm_instance = MagicMock(spec=LLMService)
            mock_llm_instance.is_api_key_available.return_value = (True, 'fake_key')
            # Simulate LLM failing for 'Other' category to force fallback to dummy 'Other' or default
            mock_llm_instance.generate_summary.return_value = None
            mock_get_llm_service.return_value = mock_llm_instance

            with patch('sys.stdout', new_callable=MagicMock):
                translator = PlainLanguageTranslator()

            expected_fallback_for_other = translator.dummy_explanations.get('Other', translator.default_summary)

            summary_none_cat = translator.translate("Some clause", None)
            self.assertEqual(summary_none_cat, expected_fallback_for_other)
            mock_llm_instance.generate_summary.assert_called_with("Some clause", "Other")
            mock_llm_instance.generate_summary.reset_mock() # Reset for next call

            summary_int_cat = translator.translate("Some clause", 123)
            self.assertEqual(summary_int_cat, expected_fallback_for_other)
            mock_llm_instance.generate_summary.assert_called_with("Some clause", "Other")

if __name__ == '__main__':
    unittest.main()
