import unittest
import hashlib
from unittest.mock import MagicMock, patch

from privacy_protocol_core.obfuscation_engine import ObfuscationEngine
from privacy_protocol_core.data_attribute import DataAttribute, ObfuscationMethod, DataCategory, SensitivityLevel
from privacy_protocol_core.policy import PrivacyPolicy, Purpose
from privacy_protocol_core.consent import UserConsent
# DataClassifier and PolicyEvaluator are needed for the main processing method
from privacy_protocol_core.data_classifier import DataClassifier
from privacy_protocol_core.policy_evaluator import PolicyEvaluator

class TestObfuscationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ObfuscationEngine()
        self.test_value_str = "sensitive_data_123"
        self.test_value_int = 12345

        # Sample attributes - Corrected with keyword arguments
        self.attr_hash = DataAttribute(attribute_name="email", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM, obfuscation_method_preferred=ObfuscationMethod.HASH)
        self.attr_redact = DataAttribute(attribute_name="ssn", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.CRITICAL, obfuscation_method_preferred=ObfuscationMethod.REDACT)
        self.attr_tokenize = DataAttribute(attribute_name="user_id", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM, obfuscation_method_preferred=ObfuscationMethod.TOKENIZE)
        self.attr_encrypt = DataAttribute(attribute_name="password", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.CRITICAL, obfuscation_method_preferred=ObfuscationMethod.ENCRYPT)
        self.attr_mask = DataAttribute(attribute_name="phone", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM, obfuscation_method_preferred=ObfuscationMethod.MASK)
        self.attr_aggregate = DataAttribute(attribute_name="age", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM, obfuscation_method_preferred=ObfuscationMethod.AGGREGATE)
        self.attr_none = DataAttribute(attribute_name="preference", category=DataCategory.USAGE_DATA, sensitivity_level=SensitivityLevel.LOW, obfuscation_method_preferred=ObfuscationMethod.NONE)


    def test_redact(self):
        self.assertEqual(self.engine._redact(self.test_value_str), "[REDACTED]")
        self.assertEqual(self.engine._redact(self.test_value_int), "[REDACTED]")

    def test_hash(self):
        hashed_str = self.engine._hash(self.test_value_str)
        self.assertIsInstance(hashed_str, str)
        self.assertEqual(len(hashed_str), 64) # SHA-256
        self.assertEqual(hashed_str, hashlib.sha256(self.test_value_str.encode('utf-8')).hexdigest())

        hashed_int = self.engine._hash(str(self.test_value_int))
        self.assertEqual(hashed_int, hashlib.sha256(str(self.test_value_int).encode('utf-8')).hexdigest())

    def test_tokenize(self):
        tokenized = self.engine._tokenize(self.test_value_str)
        self.assertTrue(tokenized.startswith("TOKEN_"))
        self.assertNotEqual(tokenized, self.engine._tokenize(self.test_value_str)) # Should be unique each time for this simple version

    def test_encrypt_placeholder(self):
        encrypted = self.engine._encrypt(self.test_value_str)
        self.assertEqual(encrypted, f"ENCRYPTED_{self.test_value_str[::-1]}")

    def test_mask(self):
        self.assertEqual(self.engine._mask("1234567890"), "******7890")
        self.assertEqual(self.engine._mask("1234567890", visible_chars=2, from_end=False), "12********")
        self.assertEqual(self.engine._mask("123", visible_chars=4), "123") # Shorter than visible_chars

    def test_aggregate_placeholder(self):
        self.assertEqual(self.engine._aggregate(self.test_value_int), "[AGGREGATED_DATA_POINT]")

    def test_obfuscate_field_consent_allows_raw(self):
        result = self.engine.obfuscate_field(self.test_value_str, self.attr_hash, True)
        self.assertEqual(result, self.test_value_str)

    def test_obfuscate_field_applies_method_when_raw_denied(self):
        # HASH
        result_hash = self.engine.obfuscate_field(self.test_value_str, self.attr_hash, False)
        self.assertEqual(result_hash, self.engine._hash(self.test_value_str))
        # REDACT
        result_redact = self.engine.obfuscate_field(self.test_value_str, self.attr_redact, False)
        self.assertEqual(result_redact, "[REDACTED]")
        # TOKENIZE
        result_tokenize = self.engine.obfuscate_field(self.test_value_str, self.attr_tokenize, False)
        self.assertTrue(result_tokenize.startswith("TOKEN_"))
        # ENCRYPT
        result_encrypt = self.engine.obfuscate_field(self.test_value_str, self.attr_encrypt, False)
        self.assertEqual(result_encrypt, self.engine._encrypt(self.test_value_str))
        # MASK
        result_mask = self.engine.obfuscate_field("1234567890", self.attr_mask, False)
        self.assertEqual(result_mask, self.engine._mask("1234567890"))
        # AGGREGATE
        result_aggregate = self.engine.obfuscate_field(100, self.attr_aggregate, False)
        self.assertEqual(result_aggregate, self.engine._aggregate(100))

    def test_obfuscate_field_none_preferred_defaults_to_redact_if_raw_denied(self):
        result = self.engine.obfuscate_field(self.test_value_str, self.attr_none, False)
        self.assertEqual(result, "[REDACTED]")

    def test_process_data_for_operation(self):
        # Mock dependencies
        mock_classifier = DataClassifier() # Use real one with some preset rules or mock its return
        mock_evaluator = PolicyEvaluator()

        # Setup: Define attributes the classifier will return for specific keys - Corrected with keyword arguments
        email_attr_for_test = DataAttribute(attribute_name="email", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM, obfuscation_method_preferred=ObfuscationMethod.HASH)
        ip_attr_for_test = DataAttribute(attribute_name="ip", category=DataCategory.TECHNICAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM, obfuscation_method_preferred=ObfuscationMethod.REDACT)
        notes_attr_for_test = DataAttribute(attribute_name="notes", category=DataCategory.OTHER, sensitivity_level=SensitivityLevel.LOW, obfuscation_method_preferred=ObfuscationMethod.NONE) # Will be redacted if raw denied

        # Mock classifier's classify_data method
        def mock_classify_data_method(data_dict):
            results = []
            if "email" in data_dict: results.append(("email", email_attr_for_test))
            if "ip" in data_dict: results.append(("ip", ip_attr_for_test))
            if "notes" in data_dict: results.append(("notes", notes_attr_for_test))
            return results
        mock_classifier.classify_data = MagicMock(side_effect=mock_classify_data_method)

        # Sample data
        raw_user_data = {
            "email": "user@example.com",
            "ip": "192.168.0.1",
            "notes": "Keep this raw"
        }

        # Policy and Consent
        test_policy = PrivacyPolicy(policy_id="p1", data_categories=[DataCategory.PERSONAL_INFO, DataCategory.TECHNICAL_INFO, DataCategory.OTHER], purposes=[Purpose.SERVICE_DELIVERY])
        test_consent = UserConsent(user_id="u1", policy_id="p1", data_categories_consented=[DataCategory.PERSONAL_INFO], purposes_consented=[Purpose.SERVICE_DELIVERY]) # Only PERSONAL_INFO for SERVICE_DELIVERY

        # Mock evaluator: email (PERSONAL_INFO) is permitted raw, ip (TECHNICAL_INFO) is not, notes (OTHER) is permitted raw
        def mock_is_operation_permitted_method(policy, consent, data_attributes, proposed_purpose, proposed_third_party=None):
            attr_name = data_attributes[0].attribute_name # Assuming one attr per call for this mock
            if attr_name == "email": return True  # Email is permitted raw
            if attr_name == "ip": return False # IP is not permitted raw
            if attr_name == "notes": return True # Notes are permitted raw
            return False
        mock_evaluator.is_operation_permitted = MagicMock(side_effect=mock_is_operation_permitted_method)

        processed_data = self.engine.process_data_for_operation(
            raw_data=raw_user_data,
            policy=test_policy,
            consent=test_consent,
            proposed_purpose=Purpose.SERVICE_DELIVERY,
            data_classifier=mock_classifier,
            policy_evaluator=mock_evaluator
        )

        self.assertEqual(processed_data["email"], "user@example.com") # Raw permitted
        self.assertEqual(processed_data["ip"], "[REDACTED]")          # Raw not permitted, REDACT preferred
        self.assertEqual(processed_data["notes"], "Keep this raw")    # Raw permitted for notes

        # Verify evaluator was called for each attribute
        self.assertEqual(mock_evaluator.is_operation_permitted.call_count, 3)
        # Verify classifier was called once
        mock_classifier.classify_data.assert_called_once_with(raw_user_data)

    def test_process_data_for_operation_input_validation(self):
        with self.assertRaisesRegex(ValueError, "raw_data must be a dictionary"):
            self.engine.process_data_for_operation("not a dict", None, None, None, None, None)


if __name__ == '__main__':
    unittest.main()
