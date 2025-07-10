# src/privacy_framework/policy.py
"""
Defines the PrivacyPolicy data structure for the Privacy Protocol.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import json
import time

# --- Enums for Policy Definition ---

class DataCategory(Enum):
    """Categorizes types of data collected."""
    PERSONAL_INFO = "Personal_Info"       # e.g., name, email, address
    USAGE_DATA = "Usage_Data"             # e.g., browsing history, app usage
    LOCATION_DATA = "Location_Data"       # e.g., GPS coordinates
    BIOMETRIC_DATA = "Biometric_Data"     # e.g., fingerprints, facial scans
    COMMUNICATION_DATA = "Communication_Data" # e.g., chat logs, call records
    FINANCIAL_DATA = "Financial_Data"     # e.g., payment info, transaction history
    HEALTH_DATA = "Health_Data"           # e.g., medical records, fitness data
    DEVICE_INFO = "Device_Info"           # e.g., IP address, device ID, OS
    OTHER = "Other"                       # Catch-all for unspecified categories

class Purpose(Enum):
    """Categorizes reasons for data collection and processing."""
    SERVICE_DELIVERY = "Service_Delivery"
    ANALYTICS = "Analytics"
    PERSONALIZATION = "Personalization"
    MARKETING = "Marketing"
    SECURITY = "Security"
    LEGAL_COMPLIANCE = "Legal_Compliance"
    RESEARCH = "Research"
    IMPROVEMENT = "Improvement" # For product/service improvement
    OPERATIONS = "Operations" # For internal operational needs
    OTHER = "Other"

class LegalBasis(Enum):
    """Legal justifications for processing data (e.g., GDPR)."""
    CONSENT = "Consent"
    CONTRACT = "Contract"
    LEGAL_OBLIGATION = "Legal_Obligation"
    VITAL_INTERESTS = "Vital_Interests"
    PUBLIC_TASK = "Public_Task"
    LEGITIMATE_INTERESTS = "Legitimate_Interests"
    NOT_APPLICABLE = "N/A" # For contexts where legal basis isn't tracked

# --- PrivacyPolicy Data Structure ---

@dataclass
class PrivacyPolicy:
    """
    Represents a machine-readable privacy policy.
    This is the system's understanding of what data is collected and why.
    """
    policy_id: str                          # Unique identifier for the policy
    version: int                            # Version number of the policy
    data_categories: List[DataCategory]     # Types of data covered by this policy
    purposes: List[Purpose]                 # Permitted purposes for data processing
    retention_period: str                   # How long data is kept (e.g., "1 year", "indefinite")
    third_parties_shared_with: List[str]    # List of entities data may be shared with
    legal_basis: LegalBasis                 # Legal basis for processing
    text_summary: str                       # Brief human-readable summary of the policy
    timestamp: int = field(default_factory=lambda: int(time.time())) # When the policy was defined

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PrivacyPolicy object to a dictionary for serialization."""
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "data_categories": [cat.value for cat in self.data_categories],
            "purposes": [purp.value for purp in self.purposes],
            "retention_period": self.retention_period,
            "third_parties_shared_with": self.third_parties_shared_with,
            "legal_basis": self.legal_basis.value,
            "text_summary": self.text_summary,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrivacyPolicy":
        """Creates a PrivacyPolicy object from a dictionary."""
        return cls(
            policy_id=data["policy_id"],
            version=data["version"],
            data_categories=[DataCategory(cat) for cat in data["data_categories"]],
            purposes=[Purpose(purp) for purp in data["purposes"]],
            retention_period=data["retention_period"],
            third_parties_shared_with=data["third_parties_shared_with"],
            legal_basis=LegalBasis(data["legal_basis"]),
            text_summary=data["text_summary"],
            timestamp=data.get("timestamp", int(time.time())) # Handle older data without timestamp
        )

    def to_json(self) -> str:
        """Converts the PrivacyPolicy object to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "PrivacyPolicy":
        """Creates a PrivacyPolicy object from a JSON string."""
        return cls.from_dict(json.loads(json_str))
