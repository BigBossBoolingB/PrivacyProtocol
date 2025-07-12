# tests/test_privacy_enforcer.py
import unittest
from unittest.mock import MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.privacy_enforcer import PrivacyEnforcer, PrivacyStatus
from src.privacy_framework.policy import PrivacyPolicy, Purpose, LegalBasis, DataCategory
from src.privacy_framework.consent import UserConsent
from src.privacy_framework.data_attribute import DataAttribute, SensitivityLevel, ObfuscationMethod
# Mocked dependencies
from src.privacy_framework.data_classifier import DataClassifier
from src.privacy_framework.policy_evaluator import PolicyEvaluator
from src.privacy_framework.obfuscation_engine import ObfuscationEngine
from src.privacy_framework.consent_manager import ConsentManager
from src.privacy_framework.policy_store import PolicyStore
from src.privacy_framework.policy_verifier import PolicyVerifier # Added for mock spec
from src.privacy_framework.data_auditor import DataTransformationAuditor # Added for mock spec


class TestPrivacyEnforcer(unittest.TestCase):

    def setUp(self):
        # Mock all dependencies
        self.mock_data_classifier = MagicMock(spec=DataClassifier)
        self.mock_policy_evaluator = MagicMock(spec=PolicyEvaluator)
        self.mock_obfuscation_engine = MagicMock(spec=ObfuscationEngine)
        self.mock_consent_manager = MagicMock(spec=ConsentManager)
        self.mock_policy_store = MagicMock(spec=PolicyStore)
        self.mock_policy_verifier = MagicMock(spec=PolicyVerifier) # Added mock for PolicyVerifier
        self.mock_auditor = MagicMock(spec=DataTransformationAuditor) # Added mock for Auditor

        self.enforcer = PrivacyEnforcer(
            data_classifier=self.mock_data_classifier,
            policy_evaluator=self.mock_policy_evaluator,
            obfuscation_engine=self.mock_obfuscation_engine,
            consent_manager=self.mock_consent_manager,
            policy_store=self.mock_policy_store,
            auditor=self.mock_auditor, # Pass auditor
            policy_verifier=self.mock_policy_verifier # Pass verifier
        )

        # Sample data commonly used in tests
        self.user_id = "user_enforcer_test"
        self.policy_id = "policy_enforcer_test"
        self.policy_version = 1
        self.raw_data_record = {"email": "test@example.com", "ip_address": "192.168.1.1"}
        self.classified_attrs = [
            DataAttribute("email", DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, True, ObfuscationMethod.HASH),
            DataAttribute("ip_address", DataCategory.DEVICE_INFO, SensitivityLevel.MEDIUM, False, ObfuscationMethod.REDACT)
        ]
        self.sample_policy = PrivacyPolicy(
            policy_id=self.policy_id, version=self.policy_version,
            data_categories=[DataCategory.PERSONAL_INFO, DataCategory.DEVICE_INFO],
            purposes=[Purpose.MARKETING, Purpose.ANALYTICS],
            legal_basis=LegalBasis.CONSENT, text_summary="Test Policy",
            retention_period="1y", third_parties_shared_with=[]
        )
        self.sample_consent = UserConsent(
            consent_id="c1", user_id=self.user_id, policy_id=self.policy_id, version=self.policy_version,
            data_categories_consented=[DataCategory.PERSONAL_INFO], purposes_consented=[Purpose.MARKETING],
            is_active=True
        )

    def test_process_data_record_no_policy(self):
        self.mock_policy_store.load_policy.return_value = None
        # Mock classifier for fallback obfuscation
        self.mock_data_classifier.classify_data.return_value = self.classified_attrs
        # Mock obfuscation engine's field-level obfuscation for the DENIED_NO_POLICY path
        self.mock_obfuscation_engine.obfuscate_field.return_value = "[FALLBACK_REDACTED]"


        result = self.enforcer.process_data_record(
            user_id=self.user_id, policy_id="unknown_policy", policy_version=1,
            data_record=self.raw_data_record, intended_purpose=Purpose.MARKETING
        )

        self.mock_policy_store.load_policy.assert_called_once_with("unknown_policy", version=1)
        self.assertEqual(result["status"], PrivacyStatus.DENIED_NO_POLICY)
        self.assertIn("Policy unknown_policy v1 not found", result["message"])
        self.assertEqual(result["processed_data"]["email"], "[FALLBACK_REDACTED]")
        self.assertEqual(result["processed_data"]["ip_address"], "[FALLBACK_REDACTED]")
        # self.mock_data_classifier.classify_data.assert_called_once_with(self.raw_data_record)
        # classify_data is called twice in this path now, once for fallback, once for audit.
        self.assertGreaterEqual(self.mock_data_classifier.classify_data.call_count, 1)


    def test_process_data_record_consent_required_but_no_consent(self):
        self.mock_policy_store.load_policy.return_value = self.sample_policy # Policy requires consent
        self.mock_consent_manager.get_active_consent.return_value = None # No consent found
        self.mock_data_classifier.classify_data.return_value = self.classified_attrs

        # Simulate obfuscation engine applying preferred methods when consent fails
        def mock_obfuscate_if_no_consent(value, method):
            if method == ObfuscationMethod.HASH: return "hashed_value"
            if method == ObfuscationMethod.REDACT: return "[REDACTED_IP]"
            return value
        self.mock_obfuscation_engine.obfuscate_field.side_effect = mock_obfuscate_if_no_consent

        result = self.enforcer.process_data_record(
            user_id=self.user_id, policy_id=self.policy_id, policy_version=self.policy_version,
            data_record=self.raw_data_record, intended_purpose=Purpose.MARKETING
        )

        self.mock_policy_store.load_policy.assert_called_once()
        self.mock_consent_manager.get_active_consent.assert_called_once_with(self.user_id, self.policy_id)
        self.assertEqual(result["status"], PrivacyStatus.DENIED_NO_CONSENT)
        self.assertEqual(result["processed_data"]["email"], "hashed_value") # Preferred obfuscation
        self.assertEqual(result["processed_data"]["ip_address"], "[REDACTED_IP]") # Preferred obfuscation


    def test_process_data_record_permitted_raw(self):
        self.mock_policy_store.load_policy.return_value = self.sample_policy
        self.mock_consent_manager.get_active_consent.return_value = self.sample_consent
        self.mock_data_classifier.classify_data.return_value = self.classified_attrs
        # Obfuscation engine's process_data_attributes returns original data if all permitted
        self.mock_obfuscation_engine.process_data_attributes.return_value = self.raw_data_record

        result = self.enforcer.process_data_record(
            user_id=self.user_id, policy_id=self.policy_id, policy_version=self.policy_version,
            data_record=self.raw_data_record, intended_purpose=Purpose.MARKETING
        )

        self.assertEqual(result["status"], PrivacyStatus.PERMITTED_RAW)
        self.assertEqual(result["processed_data"], self.raw_data_record)
        self.mock_obfuscation_engine.process_data_attributes.assert_called_once_with(
            raw_data=self.raw_data_record,
            classified_attributes=self.classified_attrs,
            policy=self.sample_policy,
            consent=self.sample_consent,
            proposed_purpose=Purpose.MARKETING,
            policy_evaluator=self.mock_policy_evaluator, # enforcer passes its own evaluator
            proposed_third_party=None
        )

    def test_process_data_record_permitted_obfuscated(self):
        self.mock_policy_store.load_policy.return_value = self.sample_policy
        self.mock_consent_manager.get_active_consent.return_value = self.sample_consent
        self.mock_data_classifier.classify_data.return_value = self.classified_attrs

        obfuscated_data = {"email": "test@example.com", "ip_address": "[REDACTED]"}
        self.mock_obfuscation_engine.process_data_attributes.return_value = obfuscated_data

        result = self.enforcer.process_data_record(
            user_id=self.user_id, policy_id=self.policy_id, policy_version=self.policy_version,
            data_record=self.raw_data_record, intended_purpose=Purpose.ANALYTICS # Assume this leads to ip obfuscation
        )

        self.assertEqual(result["status"], PrivacyStatus.PERMITTED_OBFUSCATED)
        self.assertEqual(result["processed_data"], obfuscated_data)
        self.mock_obfuscation_engine.process_data_attributes.assert_called_once()

    def test_process_data_record_policy_not_consent_basis(self):
        non_consent_policy = PrivacyPolicy(
            policy_id=self.policy_id, version=self.policy_version,
            data_categories=[DataCategory.DEVICE_INFO], purposes=[Purpose.SECURITY],
            legal_basis=LegalBasis.LEGAL_OBLIGATION, text_summary="Legal Obligation Policy",
            retention_period="1y", third_parties_shared_with=[]
        )
        self.mock_policy_store.load_policy.return_value = non_consent_policy
        self.mock_consent_manager.get_active_consent.return_value = None # Consent might be missing
        self.mock_data_classifier.classify_data.return_value = [self.classified_attrs[1]] # Only IP

        # Assume policy evaluator permits SECURITY for DEVICE_INFO without consent due to legal obligation
        self.mock_obfuscation_engine.process_data_attributes.return_value = {"ip_address": "192.168.1.1"}


        result = self.enforcer.process_data_record(
            user_id=self.user_id, policy_id=self.policy_id, policy_version=self.policy_version,
            data_record={"ip_address": "192.168.1.1"}, intended_purpose=Purpose.SECURITY
        )

        self.assertEqual(result["status"], PrivacyStatus.PERMITTED_RAW)
        self.assertEqual(result["processed_data"], {"ip_address": "192.168.1.1"})
        self.mock_consent_manager.get_active_consent.assert_called_once() # Still checks for consent
        self.mock_obfuscation_engine.process_data_attributes.assert_called_once_with(
            raw_data={"ip_address": "192.168.1.1"},
            classified_attributes=[self.classified_attrs[1]],
            policy=non_consent_policy,
            consent=None, # Consent was None
            proposed_purpose=Purpose.SECURITY,
            policy_evaluator=self.mock_policy_evaluator,
            proposed_third_party=None
        )

    def test_process_data_record_policy_verification_fails(self):
        self.mock_policy_store.load_policy.return_value = self.sample_policy
        # Simulate PolicyVerifier finding a violation
        self.mock_policy_verifier.verify_policy_adherence.return_value = {"FP00X_TEST_FAIL": False, "FP00Y_TEST_PASS": True}

        # Mock classifier for fallback obfuscation (as it's called before full denial)
        self.mock_data_classifier.classify_data.return_value = self.classified_attrs
        # Mock obfuscation engine's field-level obfuscation for the fallback
        self.mock_obfuscation_engine.obfuscate_field.side_effect = lambda value, method: f"[{method.name}_APPLIED]"


        result = self.enforcer.process_data_record(
            user_id=self.user_id, policy_id=self.policy_id, policy_version=self.policy_version,
            data_record=self.raw_data_record, intended_purpose=Purpose.MARKETING
        )

        self.mock_policy_store.load_policy.assert_called_once()
        self.mock_policy_verifier.verify_policy_adherence.assert_called_once_with(self.sample_policy)
        self.assertEqual(result["status"], PrivacyStatus.DENIED_POLICY_RESTRICTION)
        self.assertIn("failed formal verification", result["message"])
        self.assertIn("FP00X_TEST_FAIL", result["message"])

        # Check that data is obfuscated using preferred methods from classified_attrs (or REDACT if NONE)
        # Since we mocked obfuscate_field to return method name:
        # For "email", preferred is HASH. For "ip_address", preferred is REDACT.
        # _obfuscate_all_data uses preferred if not NONE, else default_method (which is HASH here).
        self.assertEqual(result["processed_data"]["email"], "[HASH_APPLIED]")
        self.assertEqual(result["processed_data"]["ip_address"], "[REDACT_APPLIED]")

        self.mock_auditor.log_event.assert_any_call(
            event_type=PrivacyStatus.DENIED_POLICY_RESTRICTION.name,
            details=unittest.mock.ANY, # Check relevant fields in details if necessary
            original_data=self.raw_data_record,
            processed_data=result["processed_data"],
            policy_id=self.policy_id
        )
        # Ensure other processing steps like consent checking or main obfuscation engine call are not reached
        self.mock_consent_manager.get_active_consent.assert_not_called()
        self.mock_obfuscation_engine.process_data_attributes.assert_not_called() # The main one, field level is called for fallback

    def test_process_data_record_policy_verification_passes(self):
        self.mock_policy_store.load_policy.return_value = self.sample_policy
        # Simulate PolicyVerifier finding no violations
        self.mock_policy_verifier.verify_policy_adherence.return_value = {"FP00X_TEST_PASS": True}

        # Continue with normal flow mocks
        self.mock_consent_manager.get_active_consent.return_value = self.sample_consent
        self.mock_data_classifier.classify_data.return_value = self.classified_attrs
        self.mock_obfuscation_engine.process_data_attributes.return_value = self.raw_data_record

        self.enforcer.process_data_record(
            user_id=self.user_id, policy_id=self.policy_id, policy_version=self.policy_version,
            data_record=self.raw_data_record, intended_purpose=Purpose.MARKETING
        )
        self.mock_policy_verifier.verify_policy_adherence.assert_called_once_with(self.sample_policy)
        # Ensure the rest of the process continues
        self.mock_consent_manager.get_active_consent.assert_called_once()
        self.mock_obfuscation_engine.process_data_attributes.assert_called_once()


if __name__ == '__main__':
    unittest.main()
