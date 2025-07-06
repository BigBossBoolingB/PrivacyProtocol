# Configuration settings for Privacy Protocol

# Example: API keys, database URIs, default settings
# For now, we'll keep it simple.
# In a real application, use environment variables or a config file parser.

# NLP Model Settings (Conceptual)
NLP_MODEL_NAME = "en_core_web_sm" # Example for SpaCy

# Risk Scoring Parameters (Conceptual)
RISK_WEIGHTS = {
    "data_selling": 0.4,
    "third_party_sharing_broad": 0.3,
    "weak_security_clause": 0.2,
    "ambiguous_language": 0.1
}

# Default user preferences (Conceptual)
DEFAULT_USER_TOLERANCE = {
    "data_sharing": "medium", # low, medium, high
    "data_retention": "medium",
    "tracking_cookies": "high"
}

# External Service URLs (Conceptual)
# Example: URL for fetching updated lists of privacy-friendly alternatives
PRIVACY_ALTERNATIVES_LIST_URL = "https://example.com/api/privacy_alternatives"

# Logging Configuration
LOG_LEVEL = "INFO" # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE_PATH = "privacy_protocol.log" # Set to None to disable file logging

# API Configuration (if applicable)
API_HOST = "0.0.0.0"
API_PORT = 8000

# Add other configuration variables as needed
# For example, paths to template files, ML model paths, etc.

# It's good practice to load sensitive info from environment variables:
# import os
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./default.db")
# API_KEY = os.getenv("THIRD_PARTY_API_KEY")
