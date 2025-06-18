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
    def test_init_api_key_available(self, mock_openai_constructor_local):
        mock_local_client = MagicMock(spec=OpenAI)
        mock_openai_constructor_local.return_value = mock_local_client

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()

        self.assertTrue(service.key_available)
        self.assertEqual(service.api_key, "key_for_init_test")
        self.assertEqual(service.client, mock_local_client)
        mock_openai_constructor_local.assert_called_once_with(api_key="key_for_init_test")

    @patch.dict(os.environ, {}, clear=True)
    @patch(OPENAI_CLIENT_PATH)
    def test_init_api_key_not_available(self, mock_openai_constructor_local):
        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        self.assertFalse(service.key_available)
        self.assertIsNone(service.api_key)
        self.assertIsNone(service.client)
        mock_openai_constructor_local.assert_not_called()

    def test_get_api_key_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout', new_callable=MagicMock):
                 service = openai_api_client.OpenAILLMService()
            self.assertEqual(service.get_api_key_env_var(), openai_api_client.OPENAI_API_KEY_ENV_VAR)

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key_for_success"})
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

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key_for_api_error"})
    @patch(OPENAI_CLIENT_PATH)
    def test_generate_summary_api_error(self, mock_openai_constructor):
        mock_client_instance = MagicMock(spec=OpenAI)
        # Try simplest APIError instantiation for side_effect
        mock_client_instance.chat.completions.create.side_effect = APIError("API Error for test", request=None, body=None) # Retaining request=None, body=None as per some signatures
        mock_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        summary = service.generate_summary("Clause here.", "Security")
        self.assertEqual(summary, "Could not generate summary due to an API error.")

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key_for_rate_limit"})
    @patch(OPENAI_CLIENT_PATH)
    def test_generate_summary_rate_limit_error(self, mock_openai_constructor):
        mock_client_instance = MagicMock(spec=OpenAI)
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.headers = MagicMock(spec=httpx.Headers)
        mock_response.headers.get.return_value = 'mock_id_rate_limit'
        # Ensure request is a MagicMock that can be passed to httpx.Response, not a direct httpx.Request
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

    @patch.dict(os.environ, {openai_api_client.OPENAI_API_KEY_ENV_VAR: "fake_key_for_empty_text"})
    @patch(OPENAI_CLIENT_PATH)
    def test_generate_summary_empty_clause_text(self, mock_openai_constructor):
        mock_openai_constructor.return_value = MagicMock(spec=OpenAI)
        with patch('sys.stdout', new_callable=MagicMock):
            service = openai_api_client.OpenAILLMService()
        summary = service.generate_summary("", "Data Collection")
        self.assertEqual(summary, "The provided clause text was empty.")

if __name__ == '__main__':
    unittest.main()
