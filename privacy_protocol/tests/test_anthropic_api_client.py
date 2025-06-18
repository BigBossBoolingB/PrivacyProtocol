import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import httpx

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.llm_services import anthropic_api_client
from anthropic import APIError, RateLimitError, Anthropic

ANTHROPIC_CLIENT_PATH = 'privacy_protocol.llm_services.anthropic_api_client.Anthropic'

class TestAnthropicLLMService(unittest.TestCase):

    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "test_anthropic_key_789"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_init_api_key_available(self, mock_anthropic_constructor):
        mock_client_instance = MagicMock(spec=Anthropic)
        mock_anthropic_constructor.return_value = mock_client_instance
        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()

        self.assertTrue(service.key_available)
        self.assertEqual(service.api_key, "test_anthropic_key_789")
        self.assertEqual(service.client, mock_client_instance)
        mock_anthropic_constructor.assert_called_once_with(api_key="test_anthropic_key_789")

    @patch.dict(os.environ, {}, clear=True)
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_init_api_key_not_available(self, mock_anthropic_constructor):
        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()
        self.assertFalse(service.key_available)
        self.assertIsNone(service.api_key)
        self.assertIsNone(service.client)
        mock_anthropic_constructor.assert_not_called()

    def test_get_api_key_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout', new_callable=MagicMock):
                service = anthropic_api_client.AnthropicLLMService()
            self.assertEqual(service.get_api_key_env_var(), anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR)

    # --- Tests for generate_summary ---
    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_generate_summary_success(self, mock_anthropic_constructor):
        mock_api_response = MagicMock()
        mock_api_response.content = [MagicMock()]
        mock_api_response.content[0].text = "Successful Anthropic summary."
        mock_api_response.stop_reason = "end_turn"

        mock_client_instance = MagicMock(spec=Anthropic)
        mock_client_instance.messages = MagicMock()
        mock_client_instance.messages.create.return_value = mock_api_response
        mock_anthropic_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()

        summary = service.generate_summary("A clause about data usage.", "Data Usage")
        self.assertEqual(summary, "Successful Anthropic summary.")
        service.client.messages.create.assert_called_once()
        call_args = service.client.messages.create.call_args
        self.assertEqual(call_args.kwargs['model'], anthropic_api_client.DEFAULT_ANTHROPIC_MODEL)
        self.assertIn("A clause about data usage.", call_args.kwargs['messages'][0]['content'])
        self.assertIn("Data Usage", call_args.kwargs['system'])
        self.assertEqual(call_args.kwargs['max_tokens'], 250)

    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_generate_summary_api_error(self, mock_anthropic_constructor):
        mock_client_instance = MagicMock(spec=Anthropic)
        mock_client_instance.messages = MagicMock()
        mock_httpx_request = MagicMock(spec=httpx.Request)
        mock_client_instance.messages.create.side_effect = APIError(
            message="API Error for test", request=mock_httpx_request, body=None
        )
        mock_anthropic_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()
        summary = service.generate_summary("Clause for API error test.", "Security")
        self.assertEqual(summary, "Could not generate summary due to an API error from the provider.")

    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_generate_summary_rate_limit_error(self, mock_anthropic_constructor):
        mock_client_instance = MagicMock(spec=Anthropic)
        mock_client_instance.messages = MagicMock()
        mock_httpx_response = MagicMock(spec=httpx.Response)
        mock_httpx_response.request = MagicMock(spec=httpx.Request)
        mock_httpx_response.status_code = 429
        mock_httpx_response.headers = MagicMock(spec=httpx.Headers)
        mock_httpx_response.headers.get.return_value = "some-retry-value"

        mock_client_instance.messages.create.side_effect = RateLimitError(
            message="Rate limit exceeded for test", response=mock_httpx_response, body=None
        )
        mock_anthropic_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()
        summary = service.generate_summary("Clause for rate limit test.", "User Rights")
        self.assertEqual(summary, "Could not generate summary due to API rate limits.")

    def test_generate_summary_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout', new_callable=MagicMock):
                service = anthropic_api_client.AnthropicLLMService()
            self.assertFalse(service.key_available)
            summary = service.generate_summary("A clause.", "Other")
            self.assertEqual(summary, "LLM service not configured: Anthropic API key missing or client failed to load.")

    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_generate_summary_empty_clause_text(self, mock_anthropic_constructor):
        mock_anthropic_constructor.return_value = MagicMock(spec=Anthropic)
        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()
        summary = service.generate_summary("", "Data Collection")
        self.assertEqual(summary, "The provided clause text was empty.")

    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_generate_summary_max_tokens_stop(self, mock_anthropic_constructor):
        mock_api_response = MagicMock()
        mock_api_response.content = [MagicMock()]
        mock_api_response.content[0].text = "Partial summary due to length."
        mock_api_response.stop_reason = "max_tokens"

        mock_client_instance = MagicMock(spec=Anthropic)
        mock_client_instance.messages = MagicMock()
        mock_client_instance.messages.create.return_value = mock_api_response
        mock_anthropic_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()
        summary = service.generate_summary("A very long clause...", "Data Usage")
        expected_summary_text = "Partial summary due to length." + "... (summary might be truncated due to length limits)"
        self.assertEqual(summary, expected_summary_text)

    # --- Tests for classify_clause ---
    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key_classify"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_classify_clause_success(self, mock_anthropic_constructor):
        mock_api_response = MagicMock()
        mock_api_response.content = [MagicMock()]
        mock_api_response.content[0].text = "Data Collection" # Exact match
        mock_api_response.stop_reason = "end_turn"

        mock_client_instance = MagicMock(spec=Anthropic)
        mock_client_instance.messages = MagicMock()
        mock_client_instance.messages.create.return_value = mock_api_response
        mock_anthropic_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()

        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("This clause is about collecting data.", categories)
        self.assertEqual(classification, "Data Collection")
        mock_client_instance.messages.create.assert_called_once()
        call_args = mock_client_instance.messages.create.call_args
        self.assertIn("Available Categories: 'Data Collection', 'Data Sharing', 'Other'", call_args.kwargs['system'])
        self.assertIn("This clause is about collecting data.", call_args.kwargs['messages'][0]['content'])

    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key_classify_parse"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_classify_clause_response_needs_parsing(self, mock_anthropic_constructor):
        mock_api_response = MagicMock()
        mock_api_response.content = [MagicMock()]
        mock_api_response.content[0].text = "The category is 'Data Sharing' for this."
        mock_api_response.stop_reason = "end_turn"

        mock_client_instance = MagicMock(spec=Anthropic)
        mock_client_instance.messages = MagicMock()
        mock_client_instance.messages.create.return_value = mock_api_response
        mock_anthropic_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("This clause is about sharing data.", categories)
        self.assertEqual(classification, "Data Sharing")

    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key_classify_none"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_classify_clause_no_valid_category_in_response(self, mock_anthropic_constructor):
        mock_api_response = MagicMock()
        mock_api_response.content = [MagicMock()]
        mock_api_response.content[0].text = "This is an unrelated answer."
        mock_api_response.stop_reason = "end_turn"

        mock_client_instance = MagicMock(spec=Anthropic)
        mock_client_instance.messages = MagicMock()
        mock_client_instance.messages.create.return_value = mock_api_response
        mock_anthropic_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("A very ambiguous clause.", categories)
        self.assertIsNone(classification)

    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key_classify_api_err"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_classify_clause_api_error(self, mock_anthropic_constructor):
        mock_client_instance = MagicMock(spec=Anthropic)
        mock_client_instance.messages = MagicMock()
        mock_httpx_request = MagicMock(spec=httpx.Request)
        mock_client_instance.messages.create.side_effect = APIError(
            message="API Error during classification", request=mock_httpx_request, body=None
        )
        mock_anthropic_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("Clause for error test.", categories)
        self.assertIsNone(classification)

    def test_classify_clause_service_unavailable(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout', new_callable=MagicMock):
                service = anthropic_api_client.AnthropicLLMService()
            self.assertFalse(service.key_available)
            categories = ["Data Collection", "Data Sharing", "Other"]
            classification = service.classify_clause("A clause.", categories)
            self.assertIsNone(classification)

    @patch.dict(os.environ, {anthropic_api_client.ANTHROPIC_API_KEY_ENV_VAR: "fake_key_classify_empty"})
    @patch(ANTHROPIC_CLIENT_PATH)
    def test_classify_clause_empty_text(self, mock_anthropic_constructor):
        mock_anthropic_constructor.return_value = MagicMock(spec=Anthropic)
        with patch('sys.stdout', new_callable=MagicMock):
            service = anthropic_api_client.AnthropicLLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("", categories)
        self.assertIsNone(classification)

if __name__ == '__main__':
    unittest.main()
