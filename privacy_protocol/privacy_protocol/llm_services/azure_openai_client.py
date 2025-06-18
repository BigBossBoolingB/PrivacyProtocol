import os
from openai import AzureOpenAI, APIError, RateLimitError # Use AzureOpenAI client
from .base_llm_service import LLMService

# Environment variables for Azure OpenAI configuration
AZURE_OPENAI_API_KEY_ENV_VAR = "AZURE_OPENAI_API_KEY"
AZURE_OPENAI_ENDPOINT_ENV_VAR = "AZURE_OPENAI_ENDPOINT"
AZURE_OPENAI_DEPLOYMENT_NAME_ENV_VAR = "AZURE_OPENAI_DEPLOYMENT_NAME"
AZURE_OPENAI_API_VERSION_ENV_VAR = "AZURE_OPENAI_API_VERSION"

# Default model is not specified here, as it's tied to the deployment name on Azure

class AzureOpenAILLMService(LLMService):
    def __init__(self):
        self.api_key: str | None = None
        self.azure_endpoint: str | None = None
        self.deployment_name: str | None = None
        self.api_version: str | None = None
        self.client: AzureOpenAI | None = None
        self.key_available: bool = False # Represents if all necessary configs are available

        config_status, retrieved_key, retrieved_endpoint, retrieved_deployment, retrieved_api_version = self.is_api_key_available()

        if config_status and retrieved_key and retrieved_endpoint and retrieved_deployment and retrieved_api_version:
            self.api_key = retrieved_key
            self.azure_endpoint = retrieved_endpoint
            self.deployment_name = retrieved_deployment
            self.api_version = retrieved_api_version
            self.key_available = True # All configs are present
            try:
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.azure_endpoint,
                    api_version=self.api_version
                )
                # Suppressed print for cleaner test logs by default:
                # if __name__ == '__main__' or os.getenv('VERBOSE_LOGGING'):
                #     print("AzureOpenAILLMService: Azure OpenAI client initialized successfully.")
            except Exception as e:
                print(f"AzureOpenAILLMService: Error initializing Azure OpenAI client: {e}. Service will be unavailable.")
                self.key_available = False
                self.client = None
        # else:
             # Warning is printed by is_api_key_available if configs are missing
             # if __name__ == '__main__' or os.getenv('VERBOSE_LOGGING'):
             #    print("AzureOpenAILLMService: One or more Azure OpenAI configuration variables not found. Service will be unavailable.")


    def get_api_key_env_var(self) -> str:
        # While Azure needs more than just a key, this is for the ABC compliance.
        # The main check is in is_api_key_available.
        return AZURE_OPENAI_API_KEY_ENV_VAR

    def is_api_key_available(self) -> tuple[bool, str | None, str | None, str | None, str | None]:
        # Returns: (all_configs_available, api_key, endpoint, deployment_name, api_version)
        api_key = os.environ.get(AZURE_OPENAI_API_KEY_ENV_VAR)
        endpoint = os.environ.get(AZURE_OPENAI_ENDPOINT_ENV_VAR)
        deployment = os.environ.get(AZURE_OPENAI_DEPLOYMENT_NAME_ENV_VAR)
        api_version = os.environ.get(AZURE_OPENAI_API_VERSION_ENV_VAR)

        if not all([api_key, endpoint, deployment, api_version]):
            missing = []
            if not api_key: missing.append(AZURE_OPENAI_API_KEY_ENV_VAR)
            if not endpoint: missing.append(AZURE_OPENAI_ENDPOINT_ENV_VAR)
            if not deployment: missing.append(AZURE_OPENAI_DEPLOYMENT_NAME_ENV_VAR)
            if not api_version: missing.append(AZURE_OPENAI_API_VERSION_ENV_VAR)
            print(f"Warning: Azure OpenAI Service missing configuration: {', '.join(missing)}")
            return False, None, None, None, None
        return True, api_key, endpoint, deployment, api_version

    def generate_summary(self, clause_text: str, ai_category: str) -> str | None:
        if not self.key_available or not self.client or not self.deployment_name:
            return "LLM service (Azure OpenAI) not configured or client not initialized. Cannot generate summary."

        if not clause_text or not clause_text.strip():
            return "The provided clause text was empty."

        try:
            system_prompt = (
                f"You are an expert at explaining complex legal text from privacy policies in simple, clear terms "
                f"for a general audience. Focus on what the clause means for the user's data or privacy. "
                f"Avoid legal jargon. Do not start with phrases like 'This clause states that...'. Get straight to the meaning."
            )
            user_prompt = (
                f"The following privacy policy clause is primarily about '{ai_category}'. "
                f"Please explain its main implications in 1-2 short, easy-to-understand sentences: "
                f"\"{clause_text}\""
            )

            chat_completion = self.client.chat.completions.create(
                model=self.deployment_name, # Use the deployment name for Azure
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )

            if chat_completion.choices and chat_completion.choices[0].message and chat_completion.choices[0].message.content:
                summary = chat_completion.choices[0].message.content.strip()
                if "cannot provide assistance" in summary.lower() or "unable to help" in summary.lower():
                    print(f"Azure OpenAI API indicated refusal for: {clause_text[:100]}...")
                    return "Could not generate summary due to content policy or other restriction from the AI."
                return summary
            else:
                if chat_completion.choices and chat_completion.choices[0].finish_reason == 'content_filter':
                    print(f"Azure OpenAI API content filter triggered for: {clause_text[:100]}...")
                    return "Could not generate summary due to Azure OpenAI content filter."
                print(f"Azure OpenAI API returned no content or unexpected structure for: {clause_text[:100]}...")
                return "Summary generation failed: No content returned." # More specific

        except RateLimitError as e:
            print(f"Azure OpenAI API rate limit exceeded: {e}")
            return "Could not generate summary due to API rate limits."
        except APIError as e:
            print(f"Azure OpenAI API error: {e}. Status: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
            return "Could not generate summary due to an API error from the provider."
        except Exception as e:
            print(f"An unexpected error occurred with Azure OpenAI API client: {e}")
            return "An unexpected error occurred with Azure OpenAI client."

if __name__ == '__main__':
    print("Azure OpenAI LLM Service Client Script - Basic Initialization Test")
    service = AzureOpenAILLMService() # Init messages (including warnings if key missing) will print here
    print(f"Azure config available (key_available flag): {service.key_available}")
    if service.key_available and service.client:
        print("Azure OpenAI client appears initialized based on key_available flag.")
        sample_clause = "Your data is processed by our servers located in the European Union and is subject to GDPR."
        sample_category = "International Data Transfer"
        print(f"\nTesting summary generation for category '{sample_category}':")
        print(f"Clause: {sample_clause}")
        summary = service.generate_summary(sample_clause, sample_category)
        if summary:
            print(f"\nAzure OpenAI Summary: {summary}")
        else:
            print("\nFailed to get summary from Azure OpenAI.")
    else:
        print("Azure OpenAI client not initialized or full config not found. Skipping live API test in __main__.")
