# src/privacy_framework/data_attribute.py
"""
Defines the DataAttribute data structure for the Privacy Protocol.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import json

# Re-import Enums from policy.py for consistency and clarity
from .policy import DataCategory # Assuming policy.py is in the same package

# --- Enums for DataAttribute ---

class SensitivityLevel(Enum):
    """Classifies the sensitivity of a data attribute."""
    LOW = "Low"         # e.g., general usage statistics
    MEDIUM = "Medium"   # e.g., device info, non-specific location
    HIGH = "High"       # e.g., precise location, browsing history
    CRITICAL = "Critical" # e.g., PII, biometric data, health records

class ObfuscationMethod(Enum):
    """Defines methods for obfuscating data."""
    REDACT = "Redact"       # Replace with [REDACTED]
    HASH = "Hash"           # Replace with cryptographic hash
    TOKENIZE = "Tokenize"   # Replace with a unique, non-identifying token
    ENCRYPT = "Encrypt"     # Placeholder for actual encryption
    MASK = "Mask"           # Partially hide (e.g., ****-1234)
    AGGREGATE = "Aggregate" # Combine with other data to hide individual details
    NONE = "None"           # No obfuscation applied

# --- DataAttribute Data Structure ---

@dataclass
class DataAttribute:
    """
    Classifies an individual piece of data based on its type, sensitivity,
    and preferred obfuscation method.
    """
    attribute_name: str                     # Name of the data field (e.g., "email", "ip_address", "health_condition")
    category: DataCategory                  # General category of the data
    sensitivity_level: SensitivityLevel     # How sensitive this specific attribute is
    is_pii: bool = False                    # True if this attribute is Personally Identifiable Information
    obfuscation_method_preferred: ObfuscationMethod = ObfuscationMethod.NONE # Default obfuscation method

    def to_dict(self) -> Dict[str, Any]:
        """Converts the DataAttribute object to a dictionary for serialization."""
        return {
            "attribute_name": self.attribute_name,
            "category": self.category.value,
            "sensitivity_level": self.sensitivity_level.value,
            "is_pii": self.is_pii,
            "obfuscation_method_preferred": self.obfuscation_method_preferred.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataAttribute":
        """Creates a DataAttribute object from a dictionary."""
        return cls(
            attribute_name=data["attribute_name"],
            category=DataCategory(data["category"]),
            sensitivity_level=SensitivityLevel(data["sensitivity_level"]),
            is_pii=data.get("is_pii", False),
            obfuscation_method_preferred=ObfuscationMethod(data.get("obfuscation_method_preferred", "None"))
        )

    def to_json(self) -> str:
        """Converts the DataAttribute object to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "DataAttribute":
        """Creates a DataAttribute object from a JSON string."""
        return cls.from_dict(json.loads(json_str))
