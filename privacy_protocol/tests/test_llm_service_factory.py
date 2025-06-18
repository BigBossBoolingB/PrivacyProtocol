import unittest
from unittest.mock import patch, MagicMock
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.llm_services import llm_service_factory
from privacy_protocol.llm_services.gemini_api_client import GeminiLLMService
from privacy_protocol.llm_services.openai_api_client import OpenAILLMService
from privacy_protocol.llm_services.anthropic_api_client import AnthropicLLMService
from privacy_protocol.llm_services.azure_openai_client import AzureOpenAILLMService

class TestLLMServiceFactory(unittest.TestCase):

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_GEMINI})
    def test_get_llm_service_gemini_from_env(self):
        mock_constructor = MagicMock(spec=GeminiLLMService)
        mock_instance = MagicMock(spec=GeminiLLMService)
        mock_instance.key_available = True
        mock_constructor.return_value = mock_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_GEMINI: mock_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertIs(service, mock_instance)
        mock_constructor.assert_called_once()

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_OPENAI})
    def test_get_llm_service_openai_from_env(self):
        mock_constructor = MagicMock(spec=OpenAILLMService)
        mock_instance = MagicMock(spec=OpenAILLMService)
        mock_instance.key_available = True
        mock_constructor.return_value = mock_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_OPENAI: mock_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertIs(service, mock_instance)
        mock_constructor.assert_called_once()

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_ANTHROPIC})
    def test_get_llm_service_anthropic_from_env(self):
        mock_constructor = MagicMock(spec=AnthropicLLMService)
        mock_instance = MagicMock(spec=AnthropicLLMService)
        mock_instance.key_available = True
        mock_constructor.return_value = mock_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_ANTHROPIC: mock_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertIs(service, mock_instance)
        mock_constructor.assert_called_once()

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_AZURE_OPENAI})
    def test_get_llm_service_azure_openai_from_env(self):
        mock_constructor = MagicMock(spec=AzureOpenAILLMService)
        mock_instance = MagicMock(spec=AzureOpenAILLMService)
        mock_instance.key_available = True
        mock_constructor.return_value = mock_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_AZURE_OPENAI: mock_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertIs(service, mock_instance)
        mock_constructor.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_get_llm_service_default_provider_gemini(self):
        self.assertEqual(llm_service_factory.DEFAULT_LLM_PROVIDER, llm_service_factory.PROVIDER_GEMINI)

        mock_constructor = MagicMock(spec=GeminiLLMService)
        mock_instance = MagicMock(spec=GeminiLLMService)
        mock_instance.key_available = True
        mock_constructor.return_value = mock_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_GEMINI: mock_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertIs(service, mock_instance)
        mock_constructor.assert_called_once()

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_GEMINI})
    def test_get_llm_service_override_env_with_openai(self):
        mock_constructor = MagicMock(spec=OpenAILLMService)
        mock_instance = MagicMock(spec=OpenAILLMService)
        mock_instance.key_available = True
        mock_constructor.return_value = mock_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_OPENAI: mock_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service(provider_name_override=llm_service_factory.PROVIDER_OPENAI)

        self.assertIs(service, mock_instance)
        mock_constructor.assert_called_once()

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_GEMINI})
    def test_get_llm_service_override_env_with_anthropic(self):
        mock_constructor = MagicMock(spec=AnthropicLLMService)
        mock_instance = MagicMock(spec=AnthropicLLMService)
        mock_instance.key_available = True
        mock_constructor.return_value = mock_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_ANTHROPIC: mock_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service(provider_name_override=llm_service_factory.PROVIDER_ANTHROPIC)

        self.assertIs(service, mock_instance)
        mock_constructor.assert_called_once()

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_GEMINI})
    def test_get_llm_service_override_env_with_azure_openai(self):
        mock_constructor = MagicMock(spec=AzureOpenAILLMService)
        mock_instance = MagicMock(spec=AzureOpenAILLMService)
        mock_instance.key_available = True
        mock_constructor.return_value = mock_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_AZURE_OPENAI: mock_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service(provider_name_override=llm_service_factory.PROVIDER_AZURE_OPENAI)

        self.assertIs(service, mock_instance)
        mock_constructor.assert_called_once()

    def test_get_llm_service_unsupported_provider_from_env(self):
        with patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: "unsupported_provider"}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()
            self.assertIsNone(service)

    def test_get_llm_service_unsupported_provider_from_override(self):
        with patch('sys.stdout', new_callable=MagicMock):
            service = llm_service_factory.get_llm_service(provider_name_override="another_unsupported_one")
        self.assertIsNone(service)

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_GEMINI})
    def test_get_llm_service_init_exception(self):
        mock_constructor_exception = MagicMock(name="MockGeminiConstructorException")
        mock_constructor_exception.side_effect = Exception("Initialization failed")

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_GEMINI: mock_constructor_exception}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertIsNone(service)
        mock_constructor_exception.assert_called_once()

if __name__ == '__main__':
    unittest.main()
