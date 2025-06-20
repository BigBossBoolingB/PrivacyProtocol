from .interpreter import PrivacyInterpreter
from .clause_categories import CLAUSE_CATEGORIES
from .ml_classifier import ClauseClassifier
from .plain_language_translator import PlainLanguageTranslator
from .user_preferences import load_user_preferences, save_user_preferences, get_default_preferences
from .recommendations_data import RECOMMENDATIONS_DATA
from .recommendations_engine import RecommendationEngine
from .llm_services import (
    LLMService, # Base class
    GeminiLLMService,
    OpenAILLMService,
    AnthropicLLMService,
    AzureOpenAILLMService,
    get_llm_service,
    ACTIVE_LLM_PROVIDER_ENV_VAR,
    DEFAULT_LLM_PROVIDER,
    PROVIDER_GEMINI,
    PROVIDER_OPENAI,
    PROVIDER_ANTHROPIC,
    PROVIDER_AZURE_OPENAI
)
# Add policy history manager functions
from .policy_history_manager import (
    save_policy_analysis,
    list_analyzed_policies,
    get_policy_analysis,
    get_latest_policy_analysis,
    generate_policy_identifier
)
from .dashboard_models import ServiceProfile, UserPrivacyProfile # Add UserPrivacyProfile
from .dashboard_data_manager import (
    load_service_profiles,
    # save_service_profiles,
    update_or_create_service_profile,
    get_all_service_profiles_for_dashboard,
    calculate_and_save_user_privacy_profile,
    load_user_privacy_profile,
    set_user_defined_name # Add this
    # get_service_id_from_source # Likely internal
)

__all__ = [
    # Core components
    'PrivacyInterpreter',
    'ClauseClassifier',
    'PlainLanguageTranslator',
    'RecommendationEngine',

    # Data modules & constants
    'CLAUSE_CATEGORIES',
    'RECOMMENDATIONS_DATA',

    # User preferences
    'load_user_preferences',
    'save_user_preferences',
    'get_default_preferences',

    # LLM Services framework
    'LLMService',
    'GeminiLLMService',
    'OpenAILLMService',
    'AnthropicLLMService',
    'AzureOpenAILLMService',
    'get_llm_service',
    'ACTIVE_LLM_PROVIDER_ENV_VAR',
    'DEFAULT_LLM_PROVIDER',
    'PROVIDER_GEMINI',
    'PROVIDER_OPENAI',
    'PROVIDER_ANTHROPIC',
    'PROVIDER_AZURE_OPENAI',

    # Policy History
    'save_policy_analysis',
    'list_analyzed_policies',
    'get_policy_analysis',
    'get_latest_policy_analysis',
    'generate_policy_identifier',

    # Dashboard components
    'ServiceProfile',
    'UserPrivacyProfile',
    'load_service_profiles',
    'update_or_create_service_profile',
    'get_all_service_profiles_for_dashboard',
    'calculate_and_save_user_privacy_profile',
    'load_user_privacy_profile',
    'set_user_defined_name', # Add this
]
