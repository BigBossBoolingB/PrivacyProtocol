import unittest
from unittest.mock import patch, MagicMock
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.llm_services.gemini_api_client import GeminiLLMService, GEMINI_API_KEY_ENV_VAR, DEFAULT_GEMINI_MODEL
from google.api_core import exceptions as google_exceptions
# genai is imported within the module being tested, so we patch it there.

# Corrected paths for mocking where genai.configure and genai.GenerativeModel are looked up
GENAI_CONFIGURE_PATH = 'privacy_protocol.llm_services.gemini_api_client.genai.configure'
GENAI_MODEL_CLASS_PATH = 'privacy_protocol.llm_services.gemini_api_client.genai.GenerativeModel'


class TestGeminiLLMService(unittest.TestCase):

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "test_api_key_123"})
    @patch(GENAI_CONFIGURE_PATH)
    @patch(GENAI_MODEL_CLASS_PATH)
    def test_init_with_api_key(self, mock_generative_model_class, mock_configure):
        mock_model_instance = MagicMock()
        mock_generative_model_class.return_value = mock_model_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()

        self.assertTrue(service.api_key_is_present)
        self.assertEqual(service.api_key, "test_api_key_123")
        mock_configure.assert_called_once_with(api_key="test_api_key_123")
        mock_generative_model_class.assert_called_once_with(DEFAULT_GEMINI_MODEL)
        self.assertEqual(service.model, mock_model_instance)

    @patch.dict(os.environ, {}, clear=True)
    @patch(GENAI_CONFIGURE_PATH)
    @patch(GENAI_MODEL_CLASS_PATH)
    def test_init_without_api_key(self, mock_generative_model_class, mock_configure):
        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()

        self.assertFalse(service.api_key_is_present)
        self.assertIsNone(service.api_key)
        mock_configure.assert_not_called()
        mock_generative_model_class.assert_not_called()
        self.assertIsNone(service.model)

    def test_get_api_key_env_var(self):
        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()
        self.assertEqual(service.get_api_key_env_var(), GEMINI_API_KEY_ENV_VAR)

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key"})
    @patch(GENAI_MODEL_CLASS_PATH)
    @patch(GENAI_CONFIGURE_PATH) # Ensure configure is also mocked for init
    def test_generate_summary_success(self, mock_configure, mock_generative_model_class):
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Successful summary."
        mock_response.parts = [MagicMock()]
        mock_response.prompt_feedback = None
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model_class.return_value = mock_model_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()

        summary = service.generate_summary("Clause text.", "Data Collection")
        self.assertEqual(summary, "Successful summary.")
        mock_model_instance.generate_content.assert_called_once()

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key"})
    @patch(GENAI_MODEL_CLASS_PATH)
    @patch(GENAI_CONFIGURE_PATH)
    def test_generate_summary_api_error(self, mock_configure, mock_generative_model_class):
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = google_exceptions.GoogleAPIError("API Error")
        mock_generative_model_class.return_value = mock_model_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()
        summary = service.generate_summary("Test clause.", "Security")
        self.assertIn("Error calling Gemini API: GoogleAPIError", summary)

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key_classify"})
    @patch(GENAI_MODEL_CLASS_PATH)
    @patch(GENAI_CONFIGURE_PATH)
    def test_classify_clause_success(self, mock_configure, mock_generative_model_class):
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Data Collection"
        mock_response.parts = [MagicMock()]
        mock_response.prompt_feedback = None
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model_class.return_value = mock_model_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()

        categories = ["Data Collection", "Data Sharing", "Other"]
        summary = service.classify_clause("This clause is about collecting data.", categories)
        self.assertEqual(summary, "Data Collection")
        mock_model_instance.generate_content.assert_called_once()
        args, _ = mock_model_instance.generate_content.call_args
        self.assertIn("Available Categories: 'Data Collection', 'Data Sharing', 'Other'", args[0])

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key_classify_parse"})
    @patch(GENAI_MODEL_CLASS_PATH)
    @patch(GENAI_CONFIGURE_PATH)
    def test_classify_clause_response_needs_parsing(self, mock_configure, mock_generative_model_class):
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "The best category is 'Data Sharing'."
        mock_response.parts = [MagicMock()]
        mock_response.prompt_feedback = None
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model_class.return_value = mock_model_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()

        categories = ["Data Collection", "Data Sharing", "Other"]
        summary = service.classify_clause("This clause is about sharing data.", categories)
        self.assertEqual(summary, "Data Sharing")

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key_classify_none"})
    @patch(GENAI_MODEL_CLASS_PATH)
    @patch(GENAI_CONFIGURE_PATH)
    def test_classify_clause_no_valid_category_in_response(self, mock_configure, mock_generative_model_class):
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is an unrelated answer."
        mock_response.parts = [MagicMock()]
        mock_response.prompt_feedback = None
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model_class.return_value = mock_model_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()

        categories = ["Data Collection", "Data Sharing", "Other"]
        summary = service.classify_clause("A very ambiguous clause.", categories)
        self.assertIsNone(summary)

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key_classify_api_err"})
    @patch(GENAI_MODEL_CLASS_PATH)
    @patch(GENAI_CONFIGURE_PATH)
    def test_classify_clause_api_error(self, mock_configure, mock_generative_model_class):
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = google_exceptions.GoogleAPIError("API Error during classification")
        mock_generative_model_class.return_value = mock_model_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        summary = service.classify_clause("Clause for error test.", categories)
        self.assertIsNone(summary)

    @patch.dict(os.environ, {}, clear=True)
    def test_classify_clause_service_unavailable(self):
        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()
        self.assertFalse(service.api_key_is_present)
        categories = ["Data Collection", "Data Sharing", "Other"]
        summary = service.classify_clause("A clause.", categories)
        self.assertIsNone(summary)

    @patch.dict(os.environ, {GEMINI_API_KEY_ENV_VAR: "fake_key_classify_empty"})
    @patch(GENAI_MODEL_CLASS_PATH)
    @patch(GENAI_CONFIGURE_PATH)
    def test_classify_clause_empty_text(self, mock_configure, mock_generative_model_class):
        mock_generative_model_class.return_value = MagicMock()
        with patch('sys.stdout', new_callable=MagicMock):
            service = GeminiLLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        summary = service.classify_clause("", categories)
        self.assertIsNone(summary)

if __name__ == '__main__':
    unittest.main()
