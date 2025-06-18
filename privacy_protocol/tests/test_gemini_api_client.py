import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.gemini_api_client import GeminiLLMService, GEMINI_API_KEY_ENV_VAR, DEFAULT_GEMINI_MODEL
from google.api_core import exceptions as google_exceptions
import google.generativeai as genai # For mocking genai.configure and genai.GenerativeModel

class TestGeminiLLMService(unittest.TestCase):

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "test_api_key_123"})
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_init_with_api_key(self, mock_generative_model_class, mock_configure):
        mock_model_instance = MagicMock()
        mock_generative_model_class.return_value = mock_model_instance

        service = GeminiLLMService()

        self.assertTrue(service.api_key_is_present)
        self.assertEqual(service.api_key, "test_api_key_123")
        mock_configure.assert_called_once_with(api_key="test_api_key_123")
        mock_generative_model_class.assert_called_once_with(DEFAULT_GEMINI_MODEL)
        self.assertEqual(service.model, mock_model_instance)

    @patch.dict(os.environ, {}, clear=True)
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_init_without_api_key(self, mock_generative_model_class, mock_configure):
        # Suppress print warning for this test
        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()

        self.assertFalse(service.api_key_is_present)
        self.assertIsNone(service.api_key)
        mock_configure.assert_not_called()
        mock_generative_model_class.assert_not_called()
        self.assertIsNone(service.model)

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "test_api_key_123"})
    def test_is_api_key_available_success(self):
        service = GeminiLLMService() # __init__ will call it
        is_available, key = service.is_api_key_available() # Call it again to check return values
        self.assertTrue(is_available)
        self.assertEqual(key, "test_api_key_123")

    @patch.dict(os.environ, {}, clear=True)
    def test_is_api_key_available_not_found(self):
        with patch('sys.stdout', new_callable=MagicMock): # Suppress warning
            service = GeminiLLMService() # __init__ will call it
            is_available, key = service.is_api_key_available()
        self.assertFalse(is_available)
        self.assertIsNone(key)

    def test_get_api_key_env_var(self):
        service = GeminiLLMService() # Doesn't matter if key exists for this test
        self.assertEqual(service.get_api_key_env_var(), GEMINI_API_KEY_ENV_VAR)

    # Tests for generate_summary
    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key"})
    @patch('google.generativeai.GenerativeModel') # Mock at class level for __init__
    def test_generate_summary_success(self, mock_gm_class_for_init):
        # Mock the model instance that would have been created in __init__
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Successful summary."
        mock_response.parts = [MagicMock()]
        mock_response.prompt_feedback = None
        mock_model_instance.generate_content.return_value = mock_response

        # Patch the genai.GenerativeModel call within __init__
        with patch('google.generativeai.GenerativeModel', return_value=mock_model_instance) as mock_gm_class:
            service = GeminiLLMService() # Re-init to use the fully mocked model
            service.model = mock_model_instance # Ensure the instance uses our mock model

        self.assertTrue(service.api_key_is_present) # Should be true due to env var patch

        summary = service.generate_summary("Clause text.", "Data Collection")
        self.assertEqual(summary, "Successful summary.")
        mock_model_instance.generate_content.assert_called_once()
        args, _ = mock_model_instance.generate_content.call_args
        self.assertIn("Clause text.", args[0])
        self.assertIn("Data Collection", args[0])


    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key"})
    def test_generate_summary_api_error(self):
        with patch('google.generativeai.GenerativeModel') as mock_gm_class:
            mock_model_instance = MagicMock()
            mock_model_instance.generate_content.side_effect = google_exceptions.GoogleAPIError("API Error")
            mock_gm_class.return_value = mock_model_instance

            service = GeminiLLMService()
            service.model = mock_model_instance # Ensure this instance uses the mock

            summary = service.generate_summary("Test clause.", "Security")
            self.assertIn("Error calling Gemini API: GoogleAPIError", summary)


    @patch.dict(os.environ, {}, clear=True) # No API Key
    def test_generate_summary_no_api_key_configured(self):
        with patch('sys.stdout', new_callable=MagicMock): # Suppress warning
            service = GeminiLLMService()
        self.assertFalse(service.api_key_is_present)
        summary = service.generate_summary("Test clause.", "User Rights")
        self.assertEqual(summary, "LLM service not configured: API key for Gemini is missing or model failed to load.")

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key"})
    def test_generate_summary_empty_clause_text(self):
        with patch('google.generativeai.GenerativeModel'): # Mock to allow init
            service = GeminiLLMService()
        summary = service.generate_summary("", "Other")
        self.assertEqual(summary, "The provided clause text was empty.")
        summary_whitespace = service.generate_summary("   ", "Other")
        self.assertEqual(summary_whitespace, "The provided clause text was empty.")


    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key"})
    def test_generate_summary_prompt_blocked(self):
        with patch('google.generativeai.GenerativeModel') as mock_gm_class:
            mock_model_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.parts = []
            mock_response.prompt_feedback = MagicMock()
            mock_response.prompt_feedback.block_reason = "SAFETY"
            mock_model_instance.generate_content.return_value = mock_response
            mock_gm_class.return_value = mock_model_instance

            service = GeminiLLMService()
            service.model = mock_model_instance

            summary = service.generate_summary("A problematic clause.", "Other")
            self.assertIn("Could not generate summary due to safety settings (Reason: SAFETY)", summary)

if __name__ == '__main__':
    unittest.main()
