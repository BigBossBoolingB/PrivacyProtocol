import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Module to test
from privacy_protocol import gemini_api_client # Corrected import
from google.api_core import exceptions as google_exceptions

class TestGeminiApiClient(unittest.TestCase):

    @patch.dict(os.environ, {gemini_api_client.GEMINI_API_KEY_ENV_VAR: "test_api_key_123"})
    def test_get_gemini_api_key_success(self):
        self.assertEqual(gemini_api_client.get_gemini_api_key(), "test_api_key_123")

    @patch.dict(os.environ, {}, clear=True) # Ensure no relevant env var
    def test_get_gemini_api_key_not_found(self):
        # Suppress print warning for this test
        with patch('sys.stdout', new_callable=MagicMock) as mock_stdout:
            self.assertIsNone(gemini_api_client.get_gemini_api_key())
            # Check if warning was printed (optional, but good)
            # self.assertTrue(any("Gemini API key not found" in call.args[0] for call in mock_stdout.write.call_args_list))

    @patch('google.generativeai.GenerativeModel') # Mock the model itself
    @patch.dict(os.environ, {gemini_api_client.GEMINI_API_KEY_ENV_VAR: "fake_key"})
    def test_generate_summary_success(self, mock_generative_model_class):
        # Configure the mock model instance and its response
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        # This matches the simpler `response.text` access path
        mock_response.text = "This is a successful Gemini summary."
        mock_response.parts = [MagicMock()] # Ensure parts exist to pass initial check
        mock_response.prompt_feedback = None # No blocking
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model_class.return_value = mock_model_instance # When GenerativeModel() is called

        summary = gemini_api_client.generate_plain_language_summary_with_gemini(
            api_key="fake_key",
            clause_text="Some clause text.",
            ai_category="Data Collection"
        )
        self.assertEqual(summary, "This is a successful Gemini summary.")
        # Check that genai.configure was called (optional, requires patching genai.configure)
        # Check that the prompt was constructed as expected (more involved, check mock_model_instance.generate_content.call_args)
        args, _ = mock_model_instance.generate_content.call_args
        self.assertIn("Clause to explain:", args[0])
        self.assertIn("Some clause text.", args[0])
        self.assertIn("Data Collection", args[0])

    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {gemini_api_client.GEMINI_API_KEY_ENV_VAR: "fake_key"})
    def test_generate_summary_api_error(self, mock_generative_model_class):
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = google_exceptions.GoogleAPIError("API Error")
        mock_generative_model_class.return_value = mock_model_instance

        summary = gemini_api_client.generate_plain_language_summary_with_gemini(
            api_key="fake_key",
            clause_text="Test clause.",
            ai_category="Security"
        )
        self.assertIsNone(summary)

    def test_generate_summary_no_api_key(self):
        summary = gemini_api_client.generate_plain_language_summary_with_gemini(
            api_key=None,
            clause_text="Test clause.",
            ai_category="User Rights"
        )
        self.assertIsNone(summary)

    def test_generate_summary_empty_clause_text(self):
        summary = gemini_api_client.generate_plain_language_summary_with_gemini(
            api_key="fake_key",
            clause_text="",
            ai_category="Other"
        )
        self.assertEqual(summary, "The provided clause text was empty.")

    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {gemini_api_client.GEMINI_API_KEY_ENV_VAR: "fake_key"})
    def test_generate_summary_prompt_blocked(self, mock_generative_model_class):
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.parts = [] # No parts if blocked this way
        mock_response.prompt_feedback = MagicMock()
        mock_response.prompt_feedback.block_reason = "SAFETY"
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model_class.return_value = mock_model_instance

        summary = gemini_api_client.generate_plain_language_summary_with_gemini(
            api_key="fake_key",
            clause_text="A potentially problematic clause.",
            ai_category="Other"
        )
        self.assertIn("Could not generate summary due to safety settings", summary)
        self.assertIn("(Reason: SAFETY)", summary)

if __name__ == '__main__':
    unittest.main()
