import uuid
import json
from datetime import datetime
# Assuming DataCategory and Purpose enums are in policy.py
# Adjust import path if structure is different or if they are moved to a common types file
try:
    from .policy import DataCategory, Purpose
except ImportError: # Handle running script directly for testing
    from policy import DataCategory, Purpose


class UserConsent:
    def __init__(self, consent_id=None, user_id=None, policy_id=None, policy_version=None,
                 data_categories_consented=None, purposes_consented=None,
                 third_parties_consented=None, timestamp=None,
                 is_active=True, signature=None, consent_source=None, expires_at=None):
        self.consent_id = consent_id if consent_id else str(uuid.uuid4())
        self.user_id = user_id # Identifier for the user
        self.policy_id = policy_id # Links to the specific PrivacyPolicy
        self.policy_version = policy_version # Version of the policy consented to

        # Granular consent choices
        self.data_categories_consented = data_categories_consented if data_categories_consented else [] # List of DataCategory enums
        self.purposes_consented = purposes_consented if purposes_consented else [] # List of Purpose enums
        self.third_parties_consented = third_parties_consented if third_parties_consented else [] # List of strings (names of third parties)

        self.timestamp = timestamp if timestamp else datetime.utcnow().isoformat()
        self.is_active = is_active # Boolean, true if this consent record is currently active
        self.signature = signature # Placeholder for cryptographic signature for verifiable consent
        self.consent_source = consent_source # E.g., "web_form_v1", "app_dialog_v2", "user_dashboard"
        self.expires_at = expires_at # Optional: ISO format string for when consent expires

    def to_dict(self):
        return {
            "consent_id": self.consent_id,
            "user_id": self.user_id,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "data_categories_consented": [dc.value for dc in self.data_categories_consented],
            "purposes_consented": [p.value for p in self.purposes_consented],
            "third_parties_consented": self.third_parties_consented,
            "timestamp": self.timestamp,
            "is_active": self.is_active,
            "signature": self.signature, # Will be None for now
            "consent_source": self.consent_source,
            "expires_at": self.expires_at
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, data):
        # Helper to safely convert string to Enum or return None if not found
        def _to_enum_list(enum_cls, values):
            if not values: return []
            return [enum_cls(v) for v in values if v in enum_cls._value2member_map_]

        return cls(
            consent_id=data.get("consent_id"),
            user_id=data.get("user_id"),
            policy_id=data.get("policy_id"),
            policy_version=data.get("policy_version"),
            data_categories_consented=_to_enum_list(DataCategory, data.get("data_categories_consented", [])),
            purposes_consented=_to_enum_list(Purpose, data.get("purposes_consented", [])),
            third_parties_consented=data.get("third_parties_consented", []),
            timestamp=data.get("timestamp"),
            is_active=data.get("is_active", True),
            signature=data.get("signature"),
            consent_source=data.get("consent_source"),
            expires_at=data.get("expires_at")
        )

    @classmethod
    def from_json(cls, json_string):
        data = json.loads(json_string)
        return cls.from_dict(data)

    def revoke(self):
        self.is_active = False
        # Potentially log this event or update timestamp of revocation
        print(f"Consent {self.consent_id} for user {self.user_id} has been revoked.")

    def __repr__(self):
        return f"<UserConsent(consent_id='{self.consent_id}', user_id='{self.user_id}', policy_id='{self.policy_id}', active={self.is_active})>"


if __name__ == '__main__':
    # Example Usage
    consent_example = UserConsent(
        user_id="user_abc_123",
        policy_id="policy_xyz_789",
        policy_version="1.1",
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
        third_parties_consented=["AnalyticsProviderX"],
        consent_source="registration_form_v1.2",
        expires_at=(datetime.utcnow() + timedelta(days=365)).isoformat() # Example: consent expires in 1 year
    )

    print("--- UserConsent Object ---")
    print(consent_example)

    print("\n--- UserConsent as Dictionary ---")
    consent_dict = consent_example.to_dict()
    print(consent_dict)

    print("\n--- UserConsent as JSON ---")
    consent_json = consent_example.to_json()
    print(consent_json)

    print("\n--- UserConsent from Dictionary ---")
    recreated_consent = UserConsent.from_dict(consent_dict)
    print(recreated_consent)
    print(f"Recreated Consented Data Categories: {recreated_consent.data_categories_consented}")

    print("\n--- UserConsent from JSON ---")
    recreated_from_json_consent = UserConsent.from_json(consent_json)
    print(recreated_from_json_consent)
    print(f"Recreated Consented Purposes: {recreated_from_json_consent.purposes_consented}")

    print("\n--- Revoking consent ---")
    recreated_from_json_consent.revoke()
    print(f"Is consent active after revocation? {recreated_from_json_consent.is_active}")

    # Test robustness of from_dict with missing enum values
    faulty_consent_dict = consent_dict.copy()
    faulty_consent_dict["data_categories_consented"].append("NonExistentCategory")
    faulty_consent_dict["purposes_consented"].append("NonExistentPurpose")
    recreated_faulty_consent = UserConsent.from_dict(faulty_consent_dict)
    print("\n--- Consent from Faulty Dictionary (should filter invalid enums) ---")
    print(f"Data Categories Consented: {recreated_faulty_consent.data_categories_consented}")
    print(f"Purposes Consented: {recreated_faulty_consent.purposes_consented}")
    assert "NonExistentCategory" not in [dc.value for dc in recreated_faulty_consent.data_categories_consented]
    assert DataCategory.PERSONAL_INFO in recreated_faulty_consent.data_categories_consented

    from datetime import timedelta # Ensure timedelta is imported for example
    print("\nAll examples executed.")
