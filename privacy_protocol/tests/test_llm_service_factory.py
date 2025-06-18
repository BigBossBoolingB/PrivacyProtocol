import unittest
from unittest.mock import patch, MagicMock
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import from the correct package level now that tests are in privacy_protocol/tests
from privacy_protocol.llm_services import llm_service_factory
from privacy_protocol.llm_services.gemini_api_client import GeminiLLMService
from privacy_protocol.llm_services.openai_api_client import OpenAILLMService

class TestLLMServiceFactory(unittest.TestCase):

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_GEMINI})
    def test_get_llm_service_gemini_from_env(self):
        mock_gemini_constructor = MagicMock(name="MockGeminiServiceConstructor")
        mock_gemini_instance = MagicMock(spec=GeminiLLMService)
        # Simulate key_available on the instance the mock constructor will return
        mock_gemini_instance.key_available = True
        mock_gemini_constructor.return_value = mock_gemini_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_GEMINI: mock_gemini_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertEqual(service, mock_gemini_instance)
        mock_gemini_constructor.assert_called_once()

    @patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_OPENAI})
    def test_get_llm_service_openai_from_env(self):
        mock_openai_constructor = MagicMock(name="MockOpenAIServiceConstructor")
        mock_openai_instance = MagicMock(spec=OpenAILLMService)
        mock_openai_instance.key_available = True
        mock_openai_constructor.return_value = mock_openai_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_OPENAI: mock_openai_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertEqual(service, mock_openai_instance)
        mock_openai_constructor.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_get_llm_service_default_provider_gemini(self):
        self.assertEqual(llm_service_factory.DEFAULT_LLM_PROVIDER, llm_service_factory.PROVIDER_GEMINI)

        mock_gemini_constructor = MagicMock(name="MockDefaultGeminiConstructor")
        mock_gemini_instance = MagicMock(spec=GeminiLLMService)
        mock_gemini_instance.key_available = True
        mock_gemini_constructor.return_value = mock_gemini_instance

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_GEMINI: mock_gemini_constructor}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertEqual(service, mock_gemini_instance)
        mock_gemini_constructor.assert_called_once()

    def test_get_llm_service_override_env_with_openai(self):
        mock_openai_constructor = MagicMock(name="MockOverrideOpenAIConstructor")
        mock_openai_instance = MagicMock(spec=OpenAILLMService)
        mock_openai_instance.key_available = True
        mock_openai_constructor.return_value = mock_openai_instance

        with patch.dict(os.environ, {llm_service_factory.ACTIVE_LLM_PROVIDER_ENV_VAR: llm_service_factory.PROVIDER_GEMINI}):
            with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_OPENAI: mock_openai_constructor}):
                with patch('sys.stdout', new_callable=MagicMock):
                    service = llm_service_factory.get_llm_service(provider_name_override=llm_service_factory.PROVIDER_OPENAI)

        self.assertEqual(service, mock_openai_instance)
        mock_openai_constructor.assert_called_once()

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
        mock_gemini_constructor_exception = MagicMock(name="MockGeminiConstructorException")
        mock_gemini_constructor_exception.side_effect = Exception("Initialization failed")

        with patch.dict(llm_service_factory.PROVIDER_MAP, {llm_service_factory.PROVIDER_GEMINI: mock_gemini_constructor_exception}):
            with patch('sys.stdout', new_callable=MagicMock):
                service = llm_service_factory.get_llm_service()

        self.assertIsNone(service)
        mock_gemini_constructor_exception.assert_called_once()

if __name__ == '__main__':
    unittest.main()
