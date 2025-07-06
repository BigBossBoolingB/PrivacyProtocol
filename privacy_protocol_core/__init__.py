# privacy_protocol_core/__init__.py

# Expose key classes and components for easier import from the library root.

# Core Data Structures
from .policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis
from .consent import UserConsent
from .data_attribute import DataAttribute, SensitivityLevel, ObfuscationMethod

# Core Functional Modules
from .interpretation.interpreter import Interpreter
from .interpretation.clause_identifier import ClauseIdentifier
from .user_management.profiles import UserProfile
from .risk_assessment.scorer import RiskScorer
from .data_tracking.policy_tracker import PolicyTracker
from .data_tracking.metadata_logger import MetadataLogger
from .action_center.recommender import Recommender
from .action_center.opt_out_navigator import OptOutNavigator
from .consent_manager import ConsentManager
from .policy_evaluator import PolicyEvaluator
from .data_classifier import DataClassifier
from .obfuscation_engine import ObfuscationEngine
from .policy_store import PolicyStore # Added
from .consent_store import ConsentStore # Added

# Main Application Orchestrator
from .main import PrivacyProtocolApp

# Configuration (if it needs to be accessed, though often not exposed at top level)
# from .config import ...

# Utilities (if any are broadly useful and safe to expose)
from .utils.helpers import sanitize_text, get_current_timestamp_iso, extract_domain

__all__ = [
    # Data Structures
    "PrivacyPolicy", "DataCategory", "Purpose", "LegalBasis",
    "UserConsent",
    "DataAttribute", "SensitivityLevel", "ObfuscationMethod",

    # Functional Modules
    "Interpreter",
    "ClauseIdentifier",
    "UserProfile",
    "RiskScorer",
    "PolicyTracker",
    "MetadataLogger",
    "Recommender",
    "OptOutNavigator",
    "ConsentManager",
    "PolicyEvaluator",
    "DataClassifier",
    "ObfuscationEngine",
    "PolicyStore", # Added
    "ConsentStore", # Added

    # Main App
    "PrivacyProtocolApp",

    # Utilities
    "sanitize_text", "get_current_timestamp_iso", "extract_domain"
]

# Optional: A version for your package
__version__ = "0.1.0-alpha"
