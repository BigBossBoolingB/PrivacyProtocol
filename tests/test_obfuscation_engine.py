# tests/test_obfuscation_engine.py
import unittest
import hashlib

# Adjust import path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.obfuscation_engine import ObfuscationEngine
from src.privacy_framework.data_attribute import DataAttribute, ObfuscationMethod, DataCategory, SensitivityLevel
from src.privacy_framework.policy import PrivacyPolicy, Purpose, LegalBasis
from src.privacy_framework.consent import UserConsent
from src.privacy_framework.policy_evaluator import PolicyEvaluator


class TestObfuscationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ObfuscationEngine()
        self.evaluator = PolicyEvaluator() # For testing process_data_attributes

        # Sample Policy
        self.test_policy = PrivacyPolicy(
            policy_id="obf_test_policy", version=1,
            data_categories=[DataCategory.PERSONAL_INFO, DataCategory.DEVICE_INFO],
            purposes=[Purpose.MARKETING, Purpose.ANALYTICS],
            legal_basis=LegalBasis.CONSENT, text_summary="Test policy for obfuscation engine",
            retention_period="1 year", # Added missing field
            third_parties_shared_with=[] # Added missing field
        )
        # Sample Consent
        self.test_consent_allow_pi_marketing = UserConsent(
            consent_id="obf_consent_001", user_id="user_obf_test",
            policy_id="obf_test_policy", version=1,
            data_categories_consented=[DataCategory.PERSONAL_INFO],
            purposes_consented=[Purpose.MARKETING],
            is_active=True
        )
        self.test_consent_deny_all_for_purpose = UserConsent(
            consent_id="obf_consent_002", user_id="user_obf_test",
            policy_id="obf_test_policy", version=1,
            data_categories_consented=[DataCategory.USAGE_DATA], # Does not include PI or Device Info
            purposes_consented=[Purpose.ANALYTICS], # Different purpose
            is_active=True
        )

    def test_obfuscate_field_redact(self):
        self.assertEqual(self.engine.obfuscate_field("secret", ObfuscationMethod.REDACT), "[REDACTED]")

    def test_obfuscate_field_hash(self):
        value = "test_value"
        expected_hash = hashlib.sha256(value.encode()).hexdigest()
        self.assertEqual(self.engine.obfuscate_field(value, ObfuscationMethod.HASH), expected_hash)
        self.assertIsNone(self.engine.obfuscate_field(None, ObfuscationMethod.HASH))


    def test_obfuscate_field_tokenize(self):
        value = "another_value"
        token = self.engine.obfuscate_field(value, ObfuscationMethod.TOKENIZE)
        self.assertTrue(token.startswith("TOKEN_"))
        self.assertEqual(len(token), len("TOKEN_") + 12) # md5[:12]
        self.assertIsNone(self.engine.obfuscate_field(None, ObfuscationMethod.TOKENIZE))

    def test_obfuscate_field_encrypt_placeholder(self):
        self.assertEqual(self.engine.obfuscate_field("clear", ObfuscationMethod.ENCRYPT), "[ENCRYPTED(clear)_PLACEHOLDER]")

    def test_obfuscate_field_mask_email(self):
        self.assertEqual(self.engine.obfuscate_field("user@example.com", ObfuscationMethod.MASK), "u****@example.com")
        self.assertEqual(self.engine.obfuscate_field("a@b.c", ObfuscationMethod.MASK), "a****@b.c") # Short username
        self.assertEqual(self.engine.obfuscate_field("nodomain", ObfuscationMethod.MASK), "no****in") # Not an email, generic rule applies

    def test_obfuscate_field_mask_generic(self):
        self.assertEqual(self.engine.obfuscate_field("1234567890", ObfuscationMethod.MASK), "12****90")
        self.assertEqual(self.engine.obfuscate_field("123", ObfuscationMethod.MASK), "1****") # Short string
        self.assertEqual(self.engine.obfuscate_field("", ObfuscationMethod.MASK), "****") # Empty string

    def test_obfuscate_field_aggregate_placeholder(self):
        self.assertEqual(self.engine.obfuscate_field(123, ObfuscationMethod.AGGREGATE), "[VALUE_FOR_AGGREGATION_ONLY]")

    def test_obfuscate_field_none(self):
        self.assertEqual(self.engine.obfuscate_field("original", ObfuscationMethod.NONE), "original")

    def test_process_data_attributes_all_permitted(self):
        raw_data = {"email": "user@example.com", "user_id": "usr123"}
        attributes = [
            DataAttribute("email", DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, True, ObfuscationMethod.HASH),
            DataAttribute("user_id", DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, True, ObfuscationMethod.REDACT)
        ]
        # Consent allows PERSONAL_INFO for MARKETING
        processed = self.engine.process_data_attributes(
            raw_data, attributes, self.test_policy, self.test_consent_allow_pi_marketing,
            Purpose.MARKETING, self.evaluator
        )
        self.assertEqual(processed["email"], "user@example.com")
        self.assertEqual(processed["user_id"], "usr123")

    def test_process_data_attributes_one_denied_applies_preferred_obfuscation(self):
        raw_data = {"email": "user@example.com", "device_id": "dev789"}
        attributes = [
            DataAttribute("email", DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, True, ObfuscationMethod.HASH),
            DataAttribute("device_id", DataCategory.DEVICE_INFO, SensitivityLevel.MEDIUM, False, ObfuscationMethod.TOKENIZE)
        ]
        # Consent allows PI for Marketing, but not DEVICE_INFO (category not in consent)
        processed = self.engine.process_data_attributes(
            raw_data, attributes, self.test_policy, self.test_consent_allow_pi_marketing,
            Purpose.MARKETING, self.evaluator
        )
        self.assertEqual(processed["email"], "user@example.com") # Permitted
        # Denied (DEVICE_INFO not in consent for MARKETING), TOKENIZE is preferred
        self.assertTrue(processed["device_id"].startswith("TOKEN_"))

    def test_process_data_attributes_denied_preferred_none_applies_default(self):
        raw_data = {"ip_address": "1.2.3.4"}
        attributes = [
            DataAttribute("ip_address", DataCategory.DEVICE_INFO, SensitivityLevel.MEDIUM, False, ObfuscationMethod.NONE)
        ]
        # Consent allows PI for Marketing, not DEVICE_INFO
        processed = self.engine.process_data_attributes(
            raw_data, attributes, self.test_policy, self.test_consent_allow_pi_marketing,
            Purpose.MARKETING, self.evaluator,
            default_obfuscation_if_denied=ObfuscationMethod.REDACT
        )
        # Denied, preferred is NONE, so default REDACT applies
        self.assertEqual(processed["ip_address"], "[REDACTED]")

    def test_process_data_attributes_purpose_not_consented(self):
        raw_data = {"email": "user@example.com"}
        attributes = [
            DataAttribute("email", DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, True, ObfuscationMethod.HASH)
        ]
        # User consented to PI for MARKETING, but purpose here is ANALYTICS (not in consent)
        processed = self.engine.process_data_attributes(
            raw_data, attributes, self.test_policy, self.test_consent_allow_pi_marketing,
            Purpose.ANALYTICS, self.evaluator
        )
        # Denied due to purpose, HASH is preferred
        self.assertEqual(processed["email"], hashlib.sha256("user@example.com".encode()).hexdigest())

    def test_process_data_attributes_unclassified_field(self):
        raw_data = {"email": "user@example.com", "unclassified_field": "sensitive_stuff"}
        attributes = [ # Only email is classified
            DataAttribute("email", DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, True, ObfuscationMethod.NONE)
        ]
        processed = self.engine.process_data_attributes(
            raw_data, attributes, self.test_policy, self.test_consent_allow_pi_marketing,
            Purpose.MARKETING, self.evaluator, default_obfuscation_if_denied=ObfuscationMethod.REDACT
        )
        self.assertEqual(processed["email"], "user@example.com") # Permitted
        self.assertEqual(processed["unclassified_field"], "[REDACTED]") # Unclassified, default redaction

if __name__ == '__main__':
    unittest.main()
