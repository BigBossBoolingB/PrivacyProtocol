import uuid
import json
from enum import Enum
# Assuming DataCategory enum is in policy.py
try:
    from .policy import DataCategory
except ImportError: # Handle running script directly for testing
    from policy import DataCategory

class SensitivityLevel(Enum):
    LOW = "Low" # e.g., preferences, browser type
    MEDIUM = "Medium" # e.g., email address, IP address, general location
    HIGH = "High" # e.g., full name, precise location, financial identifiers
    CRITICAL = "Critical" # e.g., health records, biometric data, government IDs

class ObfuscationMethod(Enum):
    NONE = "None"
    HASH = "Hash" # (SHA-256, etc.)
    REDACT = "Redact" # (Remove or replace with placeholders like XXXX)
    TOKENIZE = "Tokenize" # (Replace with a non-sensitive token)
    ENCRYPT = "Encrypt" # (AES, RSA, etc.)
    MASK = "Mask" # (Show only part of the data, e.g., last 4 digits of CC)
    AGGREGATE = "Aggregate" # (Summarize with other data, no individual values)
    ANONYMIZE = "Anonymize" # (General term for removing/modifying PII)

class DataAttribute:
    def __init__(self, attribute_id=None, attribute_name=None, category=None,
                 sensitivity_level=SensitivityLevel.MEDIUM, is_pii=None,
                 obfuscation_method_preferred=ObfuscationMethod.NONE,
                 description=""):
        self.attribute_id = attribute_id if attribute_id else str(uuid.uuid4())
        self.attribute_name = attribute_name # e.g., "email_address", "ip_address"

        if category is not None and not isinstance(category, DataCategory):
            raise ValueError(f"category must be an instance of DataCategory enum. Got {type(category)}")
        self.category = category # Links to DataCategory enum from PrivacyPolicy

        if sensitivity_level is not None and not isinstance(sensitivity_level, SensitivityLevel):
            raise ValueError(f"sensitivity_level must be an instance of SensitivityLevel enum. Got {type(sensitivity_level)}")
        self.sensitivity_level = sensitivity_level

        # Determine is_pii based on sensitivity if not explicitly set
        if is_pii is None:
            self.is_pii = self.sensitivity_level in [SensitivityLevel.MEDIUM, SensitivityLevel.HIGH, SensitivityLevel.CRITICAL]
        else:
            self.is_pii = is_pii

        if obfuscation_method_preferred is not None and not isinstance(obfuscation_method_preferred, ObfuscationMethod):
            raise ValueError(f"obfuscation_method_preferred must be an instance of ObfuscationMethod enum. Got {type(obfuscation_method_preferred)}")
        self.obfuscation_method_preferred = obfuscation_method_preferred
        self.description = description # Optional textual description of the attribute

    def to_dict(self):
        return {
            "attribute_id": self.attribute_id,
            "attribute_name": self.attribute_name,
            "category": self.category.value if self.category else None,
            "sensitivity_level": self.sensitivity_level.value if self.sensitivity_level else None,
            "is_pii": self.is_pii,
            "obfuscation_method_preferred": self.obfuscation_method_preferred.value if self.obfuscation_method_preferred else None,
            "description": self.description
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, data):
        category_val = data.get("category")
        category_enum = DataCategory(category_val) if category_val and category_val in DataCategory._value2member_map_ else None

        sensitivity_val = data.get("sensitivity_level")
        sensitivity_enum = SensitivityLevel(sensitivity_val) if sensitivity_val and sensitivity_val in SensitivityLevel._value2member_map_ else SensitivityLevel.MEDIUM

        obfuscation_val = data.get("obfuscation_method_preferred")
        obfuscation_enum = ObfuscationMethod(obfuscation_val) if obfuscation_val and obfuscation_val in ObfuscationMethod._value2member_map_ else ObfuscationMethod.NONE

        return cls(
            attribute_id=data.get("attribute_id"),
            attribute_name=data.get("attribute_name"),
            category=category_enum,
            sensitivity_level=sensitivity_enum,
            is_pii=data.get("is_pii"), # is_pii will be re-evaluated if None based on sensitivity
            obfuscation_method_preferred=obfuscation_enum,
            description=data.get("description", "")
        )

    @classmethod
    def from_json(cls, json_string):
        data = json.loads(json_string)
        return cls.from_dict(data)

    def __repr__(self):
        return f"<DataAttribute(name='{self.attribute_name}', category='{self.category.value if self.category else None}', pii={self.is_pii})>"


if __name__ == '__main__':
    # Example Usage
    email_attr = DataAttribute(
        attribute_name="user_email",
        category=DataCategory.PERSONAL_INFO,
        sensitivity_level=SensitivityLevel.MEDIUM,
        obfuscation_method_preferred=ObfuscationMethod.HASH,
        description="The primary email address of the user."
    )

    ip_attr = DataAttribute(
        attribute_name="last_login_ip",
        category=DataCategory.TECHNICAL_INFO,
        sensitivity_level=SensitivityLevel.MEDIUM, # Often considered PII
        is_pii=True # Explicitly set
    )

    pref_attr = DataAttribute(
        attribute_name="ui_theme_preference",
        category=DataCategory.USAGE_DATA,
        sensitivity_level=SensitivityLevel.LOW,
        description="User's preferred UI theme (dark/light)."
    )

    health_record_attr = DataAttribute(
        attribute_name="blood_pressure_reading",
        category=DataCategory.HEALTH_INFO,
        sensitivity_level=SensitivityLevel.CRITICAL,
        obfuscation_method_preferred=ObfuscationMethod.ENCRYPT,
        description="A specific health metric."
    )

    print("--- DataAttribute Objects ---")
    print(email_attr)
    print(ip_attr)
    print(pref_attr)
    print(health_record_attr)
    assert email_attr.is_pii == True # Auto-determined for MEDIUM
    assert pref_attr.is_pii == False # Auto-determined for LOW
    assert health_record_attr.is_pii == True # Auto-determined for CRITICAL

    print("\n--- Email Attribute as Dictionary ---")
    email_dict = email_attr.to_dict()
    print(email_dict)

    print("\n--- Email Attribute as JSON ---")
    email_json = email_attr.to_json()
    print(email_json)

    print("\n--- Attribute from Dictionary (Email) ---")
    recreated_email_attr = DataAttribute.from_dict(email_dict)
    print(recreated_email_attr)
    print(f"Recreated Category: {recreated_email_attr.category}")

    print("\n--- Attribute from JSON (Health Record) ---")
    health_json = health_record_attr.to_json()
    recreated_health_attr = DataAttribute.from_json(health_json)
    print(recreated_health_attr)
    print(f"Recreated Sensitivity: {recreated_health_attr.sensitivity_level}")

    # Test robustness with faulty enum string
    faulty_attr_dict = email_dict.copy()
    faulty_attr_dict["category"] = "NonExistentCategory"
    faulty_attr_dict["sensitivity_level"] = "NonExistentSensitivity"
    recreated_faulty_attr = DataAttribute.from_dict(faulty_attr_dict)
    print("\n--- Attribute from Faulty Dictionary ---")
    print(recreated_faulty_attr) # Should default or be None
    assert recreated_faulty_attr.category is None
    assert recreated_faulty_attr.sensitivity_level == SensitivityLevel.MEDIUM # Default for sensitivity

    # Test instantiation with invalid enum type
    try:
        DataAttribute(attribute_name="test", category="NotAnEnum")
    except ValueError as e:
        print(f"\nCaught expected error for invalid enum type: {e}")

    print("\nAll examples executed.")
