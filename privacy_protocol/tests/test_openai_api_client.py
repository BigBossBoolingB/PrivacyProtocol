import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import httpx

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.llm_services import openai_api_client
from openai import APIError, RateLimitError, OpenAI

OPENAI_CLIENT_PATH = 'privacy_protocol.llm_services.openai_api_client.OpenAI'

class TestOpenAILLMService(unittest.TestCase):

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "key_for_init_test"})
    @patch(OPENAI_CLIENT_PATH)
    def test_init_api_key_available(self, mock_openai_constructor):
        mock_client_instance = MagicMock(spec=OpenAI)
        mock_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()

        self.assertTrue(service.key_available)
        self.assertEqual(service.api_key, "key_for_init_test")
        self.assertEqual(service.client, mock_client_instance)
        mock_openai_constructor.assert_called_once_with(api_key="key_for_init_test")

    @patch.dict(os.environ, {}, clear=True)
    @patch(OPENAI_CLIENT_PATH)
    def test_init_api_key_not_available(self, mock_openai_constructor):
        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        self.assertFalse(service.key_available)
        self.assertIsNone(service.api_key)
        self.assertIsNone(service.client)
        mock_openai_constructor.assert_not_called()

    def test_get_api_key_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout', new_callable=MagicMock):
                 service = openai_api_client.OpenAILLMService()
            self.assertEqual(service.get_api_key_env_var(), openai_api_client.OPENAI_API_KEY_ENV_VAR)

    # --- Tests for generate_summary ---
    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key"})
    @patch(OPENAI_CLIENT_PATH)
    def test_generate_summary_success(self, mock_openai_constructor):
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [MagicMock()]
        mock_chat_response.choices[0].message = MagicMock()
        mock_chat_response.choices[0].message.content = "Successful OpenAI summary."

        mock_client_instance = MagicMock(spec=OpenAI)
        mock_client_instance.chat.completions.create.return_value = mock_chat_response
        mock_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()

        summary = service.generate_summary("A clause.", "Data Usage")
        self.assertEqual(summary, "Successful OpenAI summary.")
        service.client.chat.completions.create.assert_called_once()
        call_args = service.client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], openai_api_client.DEFAULT_OPENAI_MODEL)

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key"})
    @patch(OPENAI_CLIENT_PATH)
    def test_generate_summary_api_error(self, mock_openai_constructor):
        mock_client_instance = MagicMock(spec=OpenAI)
        mock_httpx_request = MagicMock(spec=httpx.Request)
        mock_client_instance.chat.completions.create.side_effect = APIError(
            message="API Error for test", request=mock_httpx_request, body=None
        )
        mock_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        summary = service.generate_summary("Clause here.", "Security")
        self.assertEqual(summary, "Could not generate summary due to an API error.")

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key"})
    @patch(OPENAI_CLIENT_PATH)
    def test_generate_summary_rate_limit_error(self, mock_openai_constructor):
        mock_client_instance = MagicMock(spec=OpenAI)
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.headers = MagicMock(spec=httpx.Headers)
        mock_response.headers.get.return_value = 'mock_id_rate_limit'
        mock_response.request = MagicMock(spec=httpx.Request)

        mock_client_instance.chat.completions.create.side_effect = RateLimitError(
            message="Rate limit exceeded for test", response=mock_response, body=None
        )
        mock_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        summary = service.generate_summary("Another clause.", "User Rights")
        self.assertEqual(summary, "Could not generate summary due to API rate limits.")

    def test_generate_summary_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout', new_callable=MagicMock):
                service = openai_api_client.OpenAILLMService()
            self.assertFalse(service.key_available)
            summary = service.generate_summary("Clause.", "Other")
            self.assertEqual(summary, "LLM service not configured: OpenAI API key missing or client failed to load.")

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key"})
    @patch(OPENAI_CLIENT_PATH)
    def test_generate_summary_empty_clause_text(self, mock_openai_constructor):
        mock_openai_constructor.return_value = MagicMock(spec=OpenAI)
        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        summary = service.generate_summary("", "Data Collection")
        self.assertEqual(summary, "The provided clause text was empty.")

    # --- Tests for classify_clause ---
    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key_classify"})
    @patch(OPENAI_CLIENT_PATH)
    def test_classify_clause_success(self, mock_openai_constructor):
        mock_choice = MagicMock()
        mock_choice.message = MagicMock()
        mock_choice.message.content = "Data Collection" # Exact match
        mock_chat_response = MagicMock(choices=[mock_choice])

        mock_client_instance = MagicMock(spec=OpenAI)
        mock_client_instance.chat.completions.create.return_value = mock_chat_response
        mock_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()

        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("This clause is about collecting data.", categories)
        self.assertEqual(classification, "Data Collection")
        mock_client_instance.chat.completions.create.assert_called_once()
        call_args = mock_client_instance.chat.completions.create.call_args
        self.assertIn("Available Categories: 'Data Collection', 'Data Sharing', 'Other'", call_args.kwargs['messages'][0]['content']) # System prompt check
        self.assertIn("This clause is about collecting data.", call_args.kwargs['messages'][1]['content']) # User prompt check

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key_classify_parse"})
    @patch(OPENAI_CLIENT_PATH)
    def test_classify_clause_response_needs_parsing(self, mock_openai_constructor):
        mock_choice = MagicMock()
        mock_choice.message = MagicMock()
        mock_choice.message.content = "The category is 'Data Sharing' for this text."
        mock_chat_response = MagicMock(choices=[mock_choice])

        mock_client_instance = MagicMock(spec=OpenAI)
        mock_client_instance.chat.completions.create.return_value = mock_chat_response
        mock_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("This clause is about sharing data.", categories)
        self.assertEqual(classification, "Data Sharing") # Expecting substring match

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key_classify_none"})
    @patch(OPENAI_CLIENT_PATH)
    def test_classify_clause_no_valid_category_in_response(self, mock_openai_constructor):
        mock_choice = MagicMock()
        mock_choice.message = MagicMock()
        mock_choice.message.content = "This is an unrelated answer."
        mock_chat_response = MagicMock(choices=[mock_choice])

        mock_client_instance = MagicMock(spec=OpenAI)
        mock_client_instance.chat.completions.create.return_value = mock_chat_response
        mock_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("A very ambiguous clause.", categories)
        self.assertIsNone(classification)

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key_classify_api_err"})
    @patch(OPENAI_CLIENT_PATH)
    def test_classify_clause_api_error(self, mock_openai_constructor):
        mock_client_instance = MagicMock(spec=OpenAI)
        mock_httpx_request = MagicMock(spec=httpx.Request)
        mock_client_instance.chat.completions.create.side_effect = APIError(
            message="API Error during classification", request=mock_httpx_request, body=None
        )
        mock_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("Clause for error test.", categories)
        self.assertIsNone(classification) # Expecting None on API error

    def test_classify_clause_service_unavailable(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout', new_callable=MagicMock):
                service = openai_api_client.OpenAILLMService()
            self.assertFalse(service.key_available)
            categories = ["Data Collection", "Data Sharing", "Other"]
            classification = service.classify_clause("A clause.", categories)
            self.assertIsNone(classification) # Expect None as service is not configured

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key_classify_empty"})
    @patch(OPENAI_CLIENT_PATH)
    def test_classify_clause_empty_text(self, mock_openai_constructor):
        mock_openai_constructor.return_value = MagicMock(spec=OpenAI)
        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("", categories)
        self.assertIsNone(classification) # Expect None for empty text

if __name__ == '__main__':
    unittest.main()
