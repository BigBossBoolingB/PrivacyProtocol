# tests/test_privacy_framework.py
import unittest
import json
import time
from src.privacy_framework.policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis
from src.privacy_framework.consent import UserConsent
from src.privacy_framework.data_attribute import DataAttribute, SensitivityLevel, ObfuscationMethod

class TestPrivacyFramework(unittest.TestCase):

    def test_data_category_enum(self):
        self.assertEqual(DataCategory.PERSONAL_INFO.value, "Personal_Info")
        self.assertIn(DataCategory.LOCATION_DATA, DataCategory)

    def test_purpose_enum(self):
        self.assertEqual(Purpose.MARKETING.value, "Marketing")
        self.assertIn(Purpose.ANALYTICS, Purpose)

    def test_legal_basis_enum(self):
        self.assertEqual(LegalBasis.CONSENT.value, "Consent")
        self.assertIn(LegalBasis.CONTRACT, LegalBasis)

    def test_sensitivity_level_enum(self):
        self.assertEqual(SensitivityLevel.CRITICAL.value, "Critical")
        self.assertIn(SensitivityLevel.LOW, SensitivityLevel)

    def test_obfuscation_method_enum(self):
        self.assertEqual(ObfuscationMethod.HASH.value, "Hash")
        self.assertIn(ObfuscationMethod.REDACT, ObfuscationMethod)

    def test_privacy_policy_creation_and_serialization(self):
        ts = int(time.time())
        policy_data = {
            "policy_id": "policy_001",
            "version": 1,
            "data_categories": [DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
            "purposes": [Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
            "retention_period": "1 year",
            "third_parties_shared_with": ["Partner A", "Service B"],
            "legal_basis": LegalBasis.CONSENT,
            "text_summary": "Collects PI and Usage for service and analytics.",
            "timestamp": ts
        }

        policy = PrivacyPolicy(**policy_data)

        self.assertEqual(policy.policy_id, "policy_001")
        self.assertEqual(policy.legal_basis, LegalBasis.CONSENT)
        self.assertEqual(len(policy.data_categories), 2)

        # Test to_dict
        policy_dict = policy.to_dict()
        self.assertEqual(policy_dict["policy_id"], "policy_001")
        self.assertEqual(policy_dict["legal_basis"], "Consent")
        self.assertEqual(policy_dict["data_categories"], ["Personal_Info", "Usage_Data"])

        # Test to_json and from_json
        policy_json = policy.to_json()
        loaded_policy = PrivacyPolicy.from_json(policy_json)
        self.assertEqual(loaded_policy.policy_id, policy.policy_id)
        self.assertEqual(loaded_policy.purposes, policy.purposes)
        self.assertEqual(loaded_policy.timestamp, policy.timestamp)

        # Test from_dict
        dict_for_from_dict = policy.to_dict() # Use the generated dict
        reloaded_policy = PrivacyPolicy.from_dict(dict_for_from_dict)
        self.assertEqual(reloaded_policy, policy)


    def test_user_consent_creation_and_serialization(self):
        ts = int(time.time())
        consent_data = {
            "consent_id": "consent_abc_123",
            "user_id": "user_x789",
            "policy_id": "policy_001",
            "version": 1,
            "data_categories_consented": [DataCategory.PERSONAL_INFO],
            "purposes_consented": [Purpose.SERVICE_DELIVERY],
            "third_parties_consented": ["Partner A"],
            "timestamp": ts,
            "is_active": True,
            "signature": "dummy_sig_placeholder",
            "obfuscation_preferences": {"email": "Hash"}
        }
        consent = UserConsent(**consent_data)

        self.assertEqual(consent.consent_id, "consent_abc_123")
        self.assertTrue(consent.is_active)
        self.assertEqual(consent.obfuscation_preferences["email"], "Hash")

        # Test to_dict
        consent_dict = consent.to_dict()
        self.assertEqual(consent_dict["consent_id"], "consent_abc_123")
        self.assertEqual(consent_dict["data_categories_consented"], ["Personal_Info"])

        # Test to_json and from_json
        consent_json = consent.to_json()
        loaded_consent = UserConsent.from_json(consent_json)
        self.assertEqual(loaded_consent.user_id, consent.user_id)
        self.assertEqual(loaded_consent.purposes_consented, consent.purposes_consented)
        self.assertEqual(loaded_consent.timestamp, consent.timestamp)

        # Test from_dict
        dict_for_from_dict = consent.to_dict()
        reloaded_consent = UserConsent.from_dict(dict_for_from_dict)
        self.assertEqual(reloaded_consent, consent)


    def test_data_attribute_creation_and_serialization(self):
        attribute_data = {
            "attribute_name": "user_email",
            "category": DataCategory.PERSONAL_INFO,
            "sensitivity_level": SensitivityLevel.CRITICAL,
            "is_pii": True,
            "obfuscation_method_preferred": ObfuscationMethod.HASH
        }
        attribute = DataAttribute(**attribute_data)

        self.assertEqual(attribute.attribute_name, "user_email")
        self.assertTrue(attribute.is_pii)
        self.assertEqual(attribute.obfuscation_method_preferred, ObfuscationMethod.HASH)

        # Test to_dict
        attribute_dict = attribute.to_dict()
        self.assertEqual(attribute_dict["attribute_name"], "user_email")
        self.assertEqual(attribute_dict["category"], "Personal_Info")

        # Test to_json and from_json
        attribute_json = attribute.to_json()
        loaded_attribute = DataAttribute.from_json(attribute_json)
        self.assertEqual(loaded_attribute.sensitivity_level, attribute.sensitivity_level)
        self.assertEqual(loaded_attribute.is_pii, attribute.is_pii)

        # Test from_dict
        dict_for_from_dict = attribute.to_dict()
        reloaded_attribute = DataAttribute.from_dict(dict_for_from_dict)
        self.assertEqual(reloaded_attribute, attribute)

if __name__ == '__main__':
    unittest.main()
