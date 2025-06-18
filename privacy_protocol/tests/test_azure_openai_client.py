import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import httpx

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.llm_services import azure_openai_client
from openai import APIError, RateLimitError, AzureOpenAI

AZURE_OPENAI_CLIENT_PATH = 'privacy_protocol.llm_services.azure_openai_client.AzureOpenAI'

class TestAzureOpenAILLMService(unittest.TestCase):

    MOCK_AZURE_ENV_VARS_VALID = {
        azure_openai_client.AZURE_OPENAI_API_KEY_ENV_VAR: "test_azure_key",
        azure_openai_client.AZURE_OPENAI_ENDPOINT_ENV_VAR: "https://test.openai.azure.com/",
        azure_openai_client.AZURE_OPENAI_DEPLOYMENT_NAME_ENV_VAR: "test-deployment",
        azure_openai_client.AZURE_OPENAI_API_VERSION_ENV_VAR: "2023-07-01-preview"
    }
    MOCK_AZURE_ENV_VARS_MISSING_KEY = MOCK_AZURE_ENV_VARS_VALID.copy()
    del MOCK_AZURE_ENV_VARS_MISSING_KEY[azure_openai_client.AZURE_OPENAI_API_KEY_ENV_VAR]

    def _create_mock_httpx_request(self):
        return MagicMock(spec=httpx.Request, method="POST", url=self.MOCK_AZURE_ENV_VARS_VALID[azure_openai_client.AZURE_OPENAI_ENDPOINT_ENV_VAR])

    def _create_mock_httpx_response(self, status_code, include_headers=False, text_body="{}", json_body=None, request=None):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = status_code
        mock_response.request = request if request else self._create_mock_httpx_request()
        mock_response.text = text_body
        mock_response.json = MagicMock(return_value=json_body if json_body is not None else {})
        if include_headers:
            mock_response.headers = MagicMock(spec=httpx.Headers)
            mock_response.headers.get.return_value = 'mock_request_id'
        else:
            mock_response.headers = {}
        return mock_response

    @patch.dict(os.environ, MOCK_AZURE_ENV_VARS_VALID)
    @patch(AZURE_OPENAI_CLIENT_PATH)
    def test_init_configs_available(self, mock_azure_openai_constructor):
        mock_client_instance = MagicMock(spec=AzureOpenAI)
        mock_azure_openai_constructor.return_value = mock_client_instance
        with patch('sys.stdout', new_callable=MagicMock):
            service = azure_openai_client.AzureOpenAILLMService()

        self.assertTrue(service.key_available)
        mock_azure_openai_constructor.assert_called_once_with(
            api_key="test_azure_key",
            azure_endpoint="https://test.openai.azure.com/",
            api_version="2023-07-01-preview"
        )

    @patch.dict(os.environ, MOCK_AZURE_ENV_VARS_MISSING_KEY)
    @patch(AZURE_OPENAI_CLIENT_PATH)
    def test_init_configs_not_fully_available(self, mock_azure_openai_constructor):
        with patch('sys.stdout', new_callable=MagicMock):
            service = azure_openai_client.AzureOpenAILLMService()
        self.assertFalse(service.key_available)
        mock_azure_openai_constructor.assert_not_called()

    def test_get_api_key_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.stdout', new_callable=MagicMock):
                service = azure_openai_client.AzureOpenAILLMService()
            self.assertEqual(service.get_api_key_env_var(), azure_openai_client.AZURE_OPENAI_API_KEY_ENV_VAR)

    @patch.dict(os.environ, MOCK_AZURE_ENV_VARS_VALID)
    @patch(AZURE_OPENAI_CLIENT_PATH)
    def test_generate_summary_success(self, mock_azure_openai_constructor):
        mock_choice = MagicMock()
        mock_choice.message = MagicMock()
        mock_choice.message.content = "Successful Azure OpenAI summary."
        mock_choice.finish_reason = "stop"
        mock_chat_response = MagicMock(choices=[mock_choice])

        mock_client_instance = MagicMock(spec=AzureOpenAI)
        mock_client_instance.chat.completions.create.return_value = mock_chat_response
        mock_azure_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = azure_openai_client.AzureOpenAILLMService()

        test_ai_category = "Data Retention"
        summary = service.generate_summary("A clause for Azure.", test_ai_category)
        self.assertEqual(summary, "Successful Azure OpenAI summary.")
        mock_client_instance.chat.completions.create.assert_called_once()

    @patch.dict(os.environ, MOCK_AZURE_ENV_VARS_VALID)
    @patch(AZURE_OPENAI_CLIENT_PATH)
    def test_generate_summary_api_error(self, mock_azure_openai_constructor):
        mock_client_instance = MagicMock(spec=AzureOpenAI)
        mock_httpx_request = self._create_mock_httpx_request()
        # Corrected: APIError takes message, request, body. Response is an attribute set on it.
        mock_client_instance.chat.completions.create.side_effect = APIError(
            message="Azure API Error for test", request=mock_httpx_request, body=None
        )
        mock_azure_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = azure_openai_client.AzureOpenAILLMService()
        summary = service.generate_summary("Clause for error.", "Other")
        self.assertEqual(summary, "Could not generate summary due to an API error from the provider.")

    @patch.dict(os.environ, MOCK_AZURE_ENV_VARS_VALID)
    @patch(AZURE_OPENAI_CLIENT_PATH)
    def test_generate_summary_rate_limit_error(self, mock_azure_openai_constructor):
        mock_client_instance = MagicMock(spec=AzureOpenAI)
        mock_httpx_response = self._create_mock_httpx_response(status_code=429, include_headers=True)
        # RateLimitError specifically takes 'response' as a keyword argument.
        mock_client_instance.chat.completions.create.side_effect = RateLimitError(
            message="Rate limit exceeded for test", response=mock_httpx_response, body=None
        )
        mock_azure_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = azure_openai_client.AzureOpenAILLMService()
        summary = service.generate_summary("Clause for rate limit.", "User Rights")
        self.assertEqual(summary, "Could not generate summary due to API rate limits.")

    @patch.dict(os.environ, MOCK_AZURE_ENV_VARS_VALID)
    @patch(AZURE_OPENAI_CLIENT_PATH)
    def test_classify_clause_success(self, mock_azure_openai_constructor):
        mock_choice = MagicMock()
        mock_choice.message = MagicMock()
        mock_choice.message.content = "Data Collection"
        mock_chat_response = MagicMock(choices=[mock_choice])

        mock_client_instance = MagicMock(spec=AzureOpenAI)
        mock_client_instance.chat.completions.create.return_value = mock_chat_response
        mock_azure_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = azure_openai_client.AzureOpenAILLMService()

        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("This clause is about collecting data.", categories)
        self.assertEqual(classification, "Data Collection")

    @patch.dict(os.environ, MOCK_AZURE_ENV_VARS_VALID)
    @patch(AZURE_OPENAI_CLIENT_PATH)
    def test_classify_clause_api_error(self, mock_azure_openai_constructor):
        mock_client_instance = MagicMock(spec=AzureOpenAI)
        mock_httpx_request = self._create_mock_httpx_request()
        mock_client_instance.chat.completions.create.side_effect = APIError(
            message="Azure API Error for classification test", request=mock_httpx_request, body=None
        )
        mock_azure_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = azure_openai_client.AzureOpenAILLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("Clause for error test.", categories)
        self.assertIsNone(classification)

    def test_classify_clause_service_unavailable(self):
        with patch.dict(os.environ, self.MOCK_AZURE_ENV_VARS_MISSING_KEY):
            with patch('sys.stdout', new_callable=MagicMock):
                service = azure_openai_client.AzureOpenAILLMService()
            self.assertFalse(service.key_available)
            categories = ["Data Collection", "Data Sharing", "Other"]
            classification = service.classify_clause("A clause.", categories)
            self.assertIsNone(classification)

    @patch.dict(os.environ, MOCK_AZURE_ENV_VARS_VALID)
    @patch(AZURE_OPENAI_CLIENT_PATH)
    def test_classify_clause_empty_text(self, mock_azure_openai_constructor):
        mock_azure_openai_constructor.return_value = MagicMock(spec=AzureOpenAI)
        with patch('sys.stdout', new_callable=MagicMock):
            service = azure_openai_client.AzureOpenAILLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("", categories)
        self.assertIsNone(classification)

    @patch.dict(os.environ, MOCK_AZURE_ENV_VARS_VALID)
    @patch(AZURE_OPENAI_CLIENT_PATH)
    def test_classify_clause_content_filter(self, mock_azure_openai_constructor):
        mock_choice = MagicMock()
        mock_choice.message = None
        mock_choice.finish_reason = "content_filter"
        mock_chat_response = MagicMock(choices=[mock_choice])

        mock_client_instance = MagicMock(spec=AzureOpenAI)
        mock_client_instance.chat.completions.create.return_value = mock_chat_response
        mock_azure_openai_constructor.return_value = mock_client_instance

        with patch('sys.stdout', new_callable=MagicMock):
            service = azure_openai_client.AzureOpenAILLMService()
        categories = ["Data Collection", "Data Sharing", "Other"]
        classification = service.classify_clause("A sensitive clause for content filter.", categories)
        self.assertEqual(classification, "Could not generate summary due to Azure OpenAI content filter.")

if __name__ == '__main__':
    unittest.main()
