import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.plain_language_translator import PlainLanguageTranslator
from privacy_protocol.clause_categories import CLAUSE_CATEGORIES

class TestPlainLanguageTranslator(unittest.TestCase):

    @patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini')
    @patch('privacy_protocol.plain_language_translator.get_gemini_api_key')
    def test_translate_with_gemini_success(self, mock_get_key, mock_generate_summary):
        mock_get_key.return_value = 'fake_api_key'
        expected_gemini_summary = "This is a fresh summary from Gemini about Data Collection."
        mock_generate_summary.return_value = expected_gemini_summary

        translator_instance = PlainLanguageTranslator()

        self.assertTrue(translator_instance.api_key_available)
        clause_text = "We collect your IP address."
        ai_category = "Data Collection"
        summary = translator_instance.translate(clause_text, ai_category)

        self.assertEqual(summary, expected_gemini_summary)
        mock_generate_summary.assert_called_once_with('fake_api_key', clause_text, ai_category)

    @patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini')
    @patch('privacy_protocol.plain_language_translator.get_gemini_api_key')
    def test_translate_gemini_api_key_not_available(self, mock_get_key, mock_generate_summary):
        mock_get_key.return_value = None

        translator_instance = PlainLanguageTranslator()

        self.assertFalse(translator_instance.api_key_available)
        clause_text = "We collect your IP address."
        ai_category = "Data Collection"
        summary = translator_instance.translate(clause_text, ai_category)

        expected_fallback_summary = translator_instance.dummy_explanations.get(ai_category)
        self.assertEqual(summary, expected_fallback_summary)
        mock_generate_summary.assert_not_called()

    @patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini')
    @patch('privacy_protocol.plain_language_translator.get_gemini_api_key')
    def test_translate_gemini_api_call_fails_returns_none(self, mock_get_key, mock_generate_summary):
        mock_get_key.return_value = 'fake_api_key'
        mock_generate_summary.return_value = None

        translator_instance = PlainLanguageTranslator()

        self.assertTrue(translator_instance.api_key_available)
        clause_text = "We share your data with partners."
        ai_category = "Data Sharing"
        summary = translator_instance.translate(clause_text, ai_category)

        expected_fallback_summary = translator_instance.dummy_explanations.get(ai_category)
        self.assertEqual(summary, expected_fallback_summary)
        mock_generate_summary.assert_called_once_with('fake_api_key', clause_text, ai_category)

    @patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini')
    @patch('privacy_protocol.plain_language_translator.get_gemini_api_key')
    def test_translate_gemini_api_call_returns_specific_error_message(self, mock_get_key, mock_generate_summary):
        mock_get_key.return_value = 'fake_api_key'
        error_message_from_client = "Could not generate summary due to safety settings (Reason: SAFETY)"
        mock_generate_summary.return_value = error_message_from_client

        translator_instance = PlainLanguageTranslator()

        self.assertTrue(translator_instance.api_key_available)
        clause_text = "A problematic clause."
        ai_category = "Data Usage"
        summary = translator_instance.translate(clause_text, ai_category)

        self.assertEqual(summary, error_message_from_client)
        mock_generate_summary.assert_called_once_with('fake_api_key', clause_text, ai_category)

    @patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini')
    @patch('privacy_protocol.plain_language_translator.get_gemini_api_key')
    def test_translate_gemini_api_returns_empty_string_uses_fallback(self, mock_get_key, mock_generate_summary):
        mock_get_key.return_value = 'fake_api_key'
        mock_generate_summary.return_value = "   "

        translator_instance = PlainLanguageTranslator()
        self.assertTrue(translator_instance.api_key_available)
        clause_text = "Some valid clause."
        ai_category = "Data Collection"
        summary = translator_instance.translate(clause_text, ai_category)

        expected_fallback_summary = translator_instance.dummy_explanations.get(ai_category)
        self.assertEqual(summary, expected_fallback_summary)
        mock_generate_summary.assert_called_once_with('fake_api_key', clause_text, ai_category)

    @patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini')
    @patch('privacy_protocol.plain_language_translator.get_gemini_api_key')
    def test_translate_empty_clause_text_returns_client_message_if_api_available(self, mock_get_key, mock_generate_summary):
        mock_get_key.return_value = 'fake_api_key'

        translator_instance = PlainLanguageTranslator()
        self.assertTrue(translator_instance.api_key_available)

        ai_category = "Data Collection"
        expected_client_message = "The provided clause text was empty."
        # Configure the mock to return the specific message when called with empty string
        def side_effect_for_empty_text(api_key, clause_text_arg, ai_category_arg):
            if not clause_text_arg.strip():
                return expected_client_message
            return "Some other summary" # Default for non-empty
        mock_generate_summary.side_effect = side_effect_for_empty_text

        summary_empty = translator_instance.translate("", ai_category)
        self.assertEqual(summary_empty, expected_client_message)
        mock_generate_summary.assert_any_call('fake_api_key', "", ai_category)

        summary_whitespace = translator_instance.translate("   ", ai_category)
        self.assertEqual(summary_whitespace, expected_client_message)
        mock_generate_summary.assert_any_call('fake_api_key', "   ", ai_category)

    def test_translate_empty_clause_text_uses_fallback_if_api_not_available(self):
        with patch('privacy_protocol.plain_language_translator.get_gemini_api_key', return_value=None):
            translator_instance = PlainLanguageTranslator()
            self.assertFalse(translator_instance.api_key_available)
            ai_category = "Data Collection"
            expected_fallback = translator_instance.dummy_explanations.get(ai_category)
            summary = translator_instance.translate("", ai_category)
            self.assertEqual(summary, expected_fallback)

    def test_translate_unknown_category_fallback(self):
        with patch('privacy_protocol.plain_language_translator.get_gemini_api_key', return_value='fake_api_key'):
            translator_instance = PlainLanguageTranslator()
            self.assertTrue(translator_instance.api_key_available)

            with patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini', return_value="Gemini summary for MadeUpCategory123") as mock_gemini_call:
                summary = translator_instance.translate("Some clause", "MadeUpCategory123")
                self.assertEqual(summary, "Gemini summary for MadeUpCategory123")
                mock_gemini_call.assert_called_once_with('fake_api_key', "Some clause", "MadeUpCategory123")

            with patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini', return_value=None) as mock_gemini_call_fail:
                summary_fail = translator_instance.translate("Some clause", "MadeUpCategory123")
                self.assertEqual(summary_fail, translator_instance.default_summary)
                mock_gemini_call_fail.assert_called_once_with('fake_api_key', "Some clause", "MadeUpCategory123")

        with patch('privacy_protocol.plain_language_translator.get_gemini_api_key', return_value=None):
            translator_instance_no_api = PlainLanguageTranslator()
            self.assertFalse(translator_instance_no_api.api_key_available)
            summary_no_api = translator_instance_no_api.translate("Some clause", "MadeUpCategory123")
            self.assertEqual(summary_no_api, translator_instance_no_api.default_summary)

    def test_all_defined_categories_have_fallback_summaries(self):
        with patch('privacy_protocol.plain_language_translator.get_gemini_api_key', return_value=None):
            translator_instance = PlainLanguageTranslator()
            self.assertFalse(translator_instance.api_key_available)
            for category in CLAUSE_CATEGORIES:
                summary = translator_instance.translate("Some clause text", category)
                self.assertIsInstance(summary, str)
                if category in translator_instance.dummy_explanations:
                    self.assertEqual(summary, translator_instance.dummy_explanations[category])
                else:
                    self.assertEqual(summary, translator_instance.default_summary)

    def test_translate_none_or_invalid_category_type_fallback(self):
        expected_gemini_summary_for_other = "Gemini thinks this is Other."

        with patch('privacy_protocol.plain_language_translator.get_gemini_api_key', return_value='fake_api_key'):
            translator_instance_api = PlainLanguageTranslator()
            dummy_fallback_for_other = translator_instance_api.dummy_explanations.get('Other', translator_instance_api.default_summary)

            # Subcase 1.1: Gemini call succeeds for 'Other' category
            with patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini', return_value=expected_gemini_summary_for_other) as mock_gemini_call_success:
                summary_none_cat_api_ok = translator_instance_api.translate("Some clause", None) # Category becomes 'Other'
                self.assertEqual(summary_none_cat_api_ok, expected_gemini_summary_for_other)
                mock_gemini_call_success.assert_called_once_with('fake_api_key', "Some clause", "Other")
                mock_gemini_call_success.reset_mock()

                summary_int_cat_api_ok = translator_instance_api.translate("Some clause", 123) # Category becomes 'Other'
                self.assertEqual(summary_int_cat_api_ok, expected_gemini_summary_for_other)
                mock_gemini_call_success.assert_called_once_with('fake_api_key', "Some clause", "Other")

            # Subcase 1.2: Gemini call fails (returns None) for 'Other' category
            with patch('privacy_protocol.plain_language_translator.generate_plain_language_summary_with_gemini', return_value=None) as mock_gemini_call_fail:
                summary_none_cat_api_fail = translator_instance_api.translate("Some clause", None)
                self.assertEqual(summary_none_cat_api_fail, dummy_fallback_for_other)
                mock_gemini_call_fail.assert_called_once_with('fake_api_key', "Some clause", "Other")
                mock_gemini_call_fail.reset_mock()

                summary_int_cat_api_fail = translator_instance_api.translate("Some clause", 123)
                self.assertEqual(summary_int_cat_api_fail, dummy_fallback_for_other)
                mock_gemini_call_fail.assert_called_once_with('fake_api_key', "Some clause", "Other")

        with patch('privacy_protocol.plain_language_translator.get_gemini_api_key', return_value=None):
            translator_instance_no_api = PlainLanguageTranslator()
            summary_none_cat_no_api = translator_instance_no_api.translate("Some clause", None)
            expected_fallback_no_api = translator_instance_no_api.dummy_explanations.get('Other', translator_instance_no_api.default_summary)
            self.assertEqual(summary_none_cat_no_api, expected_fallback_no_api)

            summary_int_cat_no_api = translator_instance_no_api.translate("Some clause", 123) # Category becomes 'Other'
            self.assertEqual(summary_int_cat_no_api, expected_fallback_no_api)

if __name__ == '__main__':
    unittest.main()
