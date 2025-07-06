import uuid
import json
from datetime import datetime
from enum import Enum

class DataCategory(Enum):
    PERSONAL_INFO = "Personal_Info" # e.g., name, email, address
    USAGE_DATA = "Usage_Data" # e.g., interactions, preferences, logs
    LOCATION_DATA = "Location_Data" # e.g., GPS, IP-based location
    BIOMETRIC_DATA = "Biometric_Data" # e.g., fingerprints, facial recognition
    FINANCIAL_INFO = "Financial_Info" # e.g., credit card details
    HEALTH_INFO = "Health_Info" # e.g., medical records, fitness data
    TECHNICAL_INFO = "Technical_Info" # e.g., IP address, device IDs, browser type
    OTHER = "Other"

class Purpose(Enum):
    SERVICE_DELIVERY = "Service_Delivery" # Core functionality
    ANALYTICS = "Analytics" # Understanding usage
    PERSONALIZATION = "Personalization" # Customizing user experience
    MARKETING = "Marketing" # Advertising, promotions
    SECURITY = "Security" # Fraud prevention, system integrity
    LEGAL_COMPLIANCE = "Legal_Compliance" # Fulfilling legal obligations
    RESEARCH_DEVELOPMENT = "Research_Development" # Improving products
    THIRD_PARTY_SHARING = "Third_Party_Sharing" # Explicitly for sharing
    OTHER = "Other"

class LegalBasis(Enum):
    CONSENT = "Consent"
    CONTRACT = "Contract"
    LEGAL_OBLIGATION = "Legal_Obligation"
    VITAL_INTERESTS = "Vital_Interests"
    PUBLIC_TASK = "Public_Task"
    LEGITIMATE_INTERESTS = "Legitimate_Interests"
    NOT_SPECIFIED = "Not_Specified"

class PrivacyPolicy:
    def __init__(self, policy_id=None, version="1.0", data_categories=None,
                 purposes=None, retention_period="Not Specified",
                 third_parties_shared_with=None, legal_basis=None,
                 text_summary="", last_updated=None):
        self.policy_id = policy_id if policy_id else str(uuid.uuid4())
        self.version = version
        self.data_categories = data_categories if data_categories else [] # List of DataCategory enums
        self.purposes = purposes if purposes else [] # List of Purpose enums
        self.retention_period = retention_period # e.g., "30 days", "Until account deletion", "Indefinite"
        self.third_parties_shared_with = third_parties_shared_with if third_parties_shared_with else [] # List of strings (names of entities)
        self.legal_basis = legal_basis if legal_basis else [] # List of LegalBasis enums
        self.text_summary = text_summary
        self.last_updated = last_updated if last_updated else datetime.utcnow().isoformat()
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "data_categories": [dc.value for dc in self.data_categories],
            "purposes": [p.value for p in self.purposes],
            "retention_period": self.retention_period,
            "third_parties_shared_with": self.third_parties_shared_with,
            "legal_basis": [lb.value for lb in self.legal_basis],
            "text_summary": self.text_summary,
            "last_updated": self.last_updated,
            "created_at": self.created_at
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, data):
        return cls(
            policy_id=data.get("policy_id"),
            version=data.get("version", "1.0"),
            data_categories=[DataCategory(dc) for dc in data.get("data_categories", []) if dc in DataCategory._value2member_map_],
            purposes=[Purpose(p) for p in data.get("purposes", []) if p in Purpose._value2member_map_],
            retention_period=data.get("retention_period", "Not Specified"),
            third_parties_shared_with=data.get("third_parties_shared_with", []),
            legal_basis=[LegalBasis(lb) for lb in data.get("legal_basis", []) if lb in LegalBasis._value2member_map_],
            text_summary=data.get("text_summary", ""),
            last_updated=data.get("last_updated")
            # created_at is set on instantiation, not typically from dict unless for reconstruction
        )

    @classmethod
    def from_json(cls, json_string):
        data = json.loads(json_string)
        return cls.from_dict(data)

    def __repr__(self):
        return f"<PrivacyPolicy(policy_id='{self.policy_id}', version='{self.version}')>"

if __name__ == '__main__':
    # Example Usage
    policy_example = PrivacyPolicy(
        version="1.1",
        data_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.TECHNICAL_INFO],
        purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS, Purpose.SECURITY],
        retention_period="90 days after account deletion",
        third_parties_shared_with=["AnalyticsProviderX", "CloudHostY"],
        legal_basis=[LegalBasis.CONTRACT, LegalBasis.LEGITIMATE_INTERESTS],
        text_summary="This policy outlines how we collect and use your data to provide our services and ensure security."
    )

    print("--- Policy Object ---")
    print(policy_example)

    print("\n--- Policy as Dictionary ---")
    policy_dict = policy_example.to_dict()
    print(policy_dict)

    print("\n--- Policy as JSON ---")
    policy_json = policy_example.to_json()
    print(policy_json)

    print("\n--- Policy from Dictionary ---")
    recreated_policy = PrivacyPolicy.from_dict(policy_dict)
    print(recreated_policy)
    print(f"Recreated Data Categories: {recreated_policy.data_categories}")

    print("\n--- Policy from JSON ---")
    recreated_from_json_policy = PrivacyPolicy.from_json(policy_json)
    print(recreated_from_json_policy)
    print(f"Recreated Purposes: {recreated_from_json_policy.purposes}")

    # Test robustness of from_dict with missing enum values
    faulty_dict = policy_dict.copy()
    faulty_dict["data_categories"].append("NonExistentCategory")
    faulty_dict["purposes"].append("NonExistentPurpose")
    recreated_faulty_policy = PrivacyPolicy.from_dict(faulty_dict)
    print("\n--- Policy from Faulty Dictionary (should filter invalid enums) ---")
    print(f"Data Categories: {recreated_faulty_policy.data_categories}") # Should not contain NonExistentCategory
    print(f"Purposes: {recreated_faulty_policy.purposes}") # Should not contain NonExistentPurpose
    assert "NonExistentCategory" not in [dc.value for dc in recreated_faulty_policy.data_categories]
    assert DataCategory.PERSONAL_INFO in recreated_faulty_policy.data_categories
    assert Purpose.SERVICE_DELIVERY in recreated_faulty_policy.purposes

    print("\nAll examples executed.")
