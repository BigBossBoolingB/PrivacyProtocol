import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, Tuple, Optional, List # Added Optional and List

from privacy_protocol_core.privacy_enforcer import PrivacyEnforcer
from privacy_protocol_core.policy import PrivacyPolicy, Purpose, DataCategory, LegalBasis
from privacy_protocol_core.consent import UserConsent
from privacy_protocol_core.data_attribute import DataAttribute, ObfuscationMethod, SensitivityLevel

# Import actual classes for specing MagicMock correctly
from privacy_protocol_core.policy_store import PolicyStore
from privacy_protocol_core.consent_manager import ConsentManager
from privacy_protocol_core.data_classifier import DataClassifier
from privacy_protocol_core.policy_evaluator import PolicyEvaluator
from privacy_protocol_core.obfuscation_engine import ObfuscationEngine
# Import DataTransformationAuditor for spec and type hinting
try:
    from privacy_protocol_core.auditing.data_auditor import DataTransformationAuditor
except ImportError: # Define dummy if not found, for robustness if tests run before auditor exists
    class DataTransformationAuditor:
        def log_event(self, *args, **kwargs): pass
        @staticmethod
        def hash_data(data): return "dummy_hash"


class TestPrivacyEnforcer(unittest.TestCase):

    def setUp(self):
        # Use the actual classes for the spec argument
        self.mock_policy_store = MagicMock(spec=PolicyStore)
        self.mock_consent_manager = MagicMock(spec=ConsentManager)
        self.mock_data_classifier = MagicMock(spec=DataClassifier)
        self.mock_policy_evaluator = MagicMock(spec=PolicyEvaluator)
        self.mock_obfuscation_engine = MagicMock(spec=ObfuscationEngine)
        self.mock_auditor = MagicMock(spec=DataTransformationAuditor)

        # Mock the static method hash_data if it's called directly by enforcer (it is)
        # If it's not part of the spec for MagicMock(spec=DataTransformationAuditor)
        # For this test, ensure the mock_auditor instance has hash_data
        self.mock_auditor.hash_data = MagicMock(return_value="mocked_hash_value")


        self.enforcer = PrivacyEnforcer(
            policy_store=self.mock_policy_store,
            consent_manager=self.mock_consent_manager,
            data_classifier=self.mock_data_classifier,
            policy_evaluator=self.mock_policy_evaluator,
            obfuscation_engine=self.mock_obfuscation_engine,
            auditor=self.mock_auditor # Pass the mocked auditor
        )

        # Sample data for use in tests
        self.user_id = "user123"
        self.policy_id = "policyABC"
        self.policy_version = "1.0"
        self.raw_data_record = {"email": "test@example.com", "ip": "127.0.0.1"}
        self.intended_purpose = Purpose.SERVICE_DELIVERY

        self.sample_policy = PrivacyPolicy(policy_id=self.policy_id, version=self.policy_version)
        self.sample_consent = UserConsent(user_id=self.user_id, policy_id=self.policy_id, policy_version=self.policy_version, is_active=True)


    def test_process_data_policy_not_found(self):
        self.mock_policy_store.load_policy.return_value = None

        processed_data, status = self.enforcer.process_data_record(
            self.user_id, self.policy_id, self.policy_version, self.raw_data_record, self.intended_purpose
        )

        self.assertEqual(status, "Policy_Not_Found")
        self.assertEqual(processed_data, self.raw_data_record) # Should return original data
        self.mock_policy_store.load_policy.assert_called_once_with(self.policy_id, version=self.policy_version)
        self.mock_consent_manager.get_active_consent.assert_not_called()
        self.mock_obfuscation_engine.process_data_for_operation.assert_not_called()
        # Verify auditor was called for policy failure
        self.mock_auditor.log_event.assert_called_once()
        args, kwargs = self.mock_auditor.log_event.call_args
        self.assertEqual(kwargs.get("event_type"), "POLICY_ACCESS_FAILURE")
        self.assertEqual(kwargs.get("status"), "Policy_Not_Found")


    def test_process_data_no_active_consent(self):
        self.mock_policy_store.load_policy.return_value = self.sample_policy
        self.mock_consent_manager.get_active_consent.return_value = None # No active consent

        # Mock ObfuscationEngine to return a transformed dict when no consent
        transformed_due_to_no_consent = {k: "[OBFUSCATED_NO_CONSENT]" for k in self.raw_data_record}
        self.mock_obfuscation_engine.process_data_for_operation.return_value = transformed_due_to_no_consent

        processed_data, status = self.enforcer.process_data_record(
            self.user_id, self.policy_id, self.policy_version, self.raw_data_record, self.intended_purpose
        )

        self.assertTrue(status.startswith("Transformed_Fallback_")) # Corrected status check
        self.assertEqual(processed_data, transformed_due_to_no_consent)
        self.mock_policy_store.load_policy.assert_called_once_with(self.policy_id, version=self.policy_version)
        self.mock_consent_manager.get_active_consent.assert_called_once_with(self.user_id, self.policy_id)
        # Check that process_data_for_operation was called with consent=None
        self.mock_obfuscation_engine.process_data_for_operation.assert_called_once_with(
            raw_data=self.raw_data_record,
            policy=self.sample_policy,
            consent=None, # Crucial check
            proposed_purpose=self.intended_purpose,
            data_classifier=self.mock_data_classifier,
            policy_evaluator=self.mock_policy_evaluator,
            proposed_third_party=None
        )
        # Verify auditor was called for consent failure
        self.mock_auditor.log_event.assert_called_once()
        args, kwargs = self.mock_auditor.log_event.call_args
        self.assertEqual(kwargs.get("event_type"), "CONSENT_VALIDATION_OUTCOME")
        self.assertTrue(kwargs.get("status").startswith("Transformed_Fallback_"), f"Actual status: {kwargs.get('status')}")


    def test_process_data_allowed_raw(self):
        self.mock_policy_store.load_policy.return_value = self.sample_policy
        self.mock_consent_manager.get_active_consent.return_value = self.sample_consent

        # Mock ObfuscationEngine to return original data (signifying raw access permitted)
        self.mock_obfuscation_engine.process_data_for_operation.return_value = self.raw_data_record

        processed_data, status = self.enforcer.process_data_record(
            self.user_id, self.policy_id, self.policy_version, self.raw_data_record, self.intended_purpose
        )

        self.assertEqual(status, "Allowed_Raw_With_Consent") # Corrected status
        self.assertEqual(processed_data, self.raw_data_record)
        self.mock_obfuscation_engine.process_data_for_operation.assert_called_once_with(
            raw_data=self.raw_data_record, policy=self.sample_policy, consent=self.sample_consent,
            proposed_purpose=self.intended_purpose, data_classifier=self.mock_data_classifier,
            policy_evaluator=self.mock_policy_evaluator, proposed_third_party=None
        )
        # Verify auditor was called for successful raw processing
        self.mock_auditor.log_event.assert_called_once()
        args, kwargs = self.mock_auditor.log_event.call_args
        self.assertEqual(kwargs.get("event_type"), "DATA_PROCESSED_WITH_VALID_CONSENT")
        self.assertEqual(kwargs.get("status"), "Allowed_Raw_With_Consent") # Corrected expected audit status

    def test_process_data_allowed_transformed(self):
        self.mock_policy_store.load_policy.return_value = self.sample_policy
        self.mock_consent_manager.get_active_consent.return_value = self.sample_consent

        transformed_data = {"email": "[HASHED_EMAIL]", "ip": "[REDACTED_IP]"}
        # Mock ObfuscationEngine to return transformed data
        self.mock_obfuscation_engine.process_data_for_operation.return_value = transformed_data

        processed_data, status = self.enforcer.process_data_record(
            self.user_id, self.policy_id, self.policy_version, self.raw_data_record, self.intended_purpose
        )

        self.assertEqual(status, "Allowed_Transformed_With_Consent") # Corrected status
        self.assertEqual(processed_data, transformed_data)
        self.mock_obfuscation_engine.process_data_for_operation.assert_called_once_with(
            raw_data=self.raw_data_record, policy=self.sample_policy, consent=self.sample_consent,
            proposed_purpose=self.intended_purpose, data_classifier=self.mock_data_classifier,
            policy_evaluator=self.mock_policy_evaluator, proposed_third_party=None
        )
        # Verify auditor was called for successful transformed processing
        self.mock_auditor.log_event.assert_called_once()
        args, kwargs = self.mock_auditor.log_event.call_args
        self.assertEqual(kwargs.get("event_type"), "DATA_PROCESSED_WITH_VALID_CONSENT")
        self.assertEqual(kwargs.get("status"), "Allowed_Transformed_With_Consent") # Corrected expected audit status

    def test_process_data_consent_version_mismatch_results_in_transformation_and_audit(self):
        # Scenario where active consent is for a different policy version than loaded policy
        # This test primarily checks if the warning path in PrivacyEnforcer is exercised,
        # leading to consent being treated as None, and data transformed.
        # The actual behavior (strict denial vs. proceeding) depends on refined logic.
        # Current enforcer proceeds but a warning would be printed if prints were on.

        policy_v1 = PrivacyPolicy(policy_id=self.policy_id, version="1.0")
        policy_v2 = PrivacyPolicy(policy_id=self.policy_id, version="2.0") # Policy we intend to use

        consent_for_v1 = UserConsent(user_id=self.user_id, policy_id=self.policy_id, policy_version="1.0", is_active=True)

        self.mock_policy_store.load_policy.return_value = policy_v2 # Loading v2 of policy
        self.mock_consent_manager.get_active_consent.return_value = consent_for_v1 # But active consent is for v1

        # Assume it proceeds and leads to transformation
        transformed_data = {"email": "[TRANSFORMED]", "ip": "[TRANSFORMED]"}
        self.mock_obfuscation_engine.process_data_for_operation.return_value = transformed_data

        processed_data, status = self.enforcer.process_data_record(
            self.user_id, self.policy_id, "2.0", self.raw_data_record, self.intended_purpose
        )

        # Expect data to be transformed as consent is invalidated due to version mismatch
        self.assertTrue(status.startswith("Transformed_Fallback_"))
        self.assertEqual(processed_data, transformed_data)

        # Verify ObfuscationEngine was called with consent=None
        call_args = self.mock_obfuscation_engine.process_data_for_operation.call_args
        self.assertIsNone(call_args[1].get('consent')) # Check kwargs for consent=None

        # Verify auditor was called for consent validation failure
        self.mock_auditor.log_event.assert_called_once()
        args, audit_kwargs = self.mock_auditor.log_event.call_args
        self.assertEqual(audit_kwargs.get("event_type"), "CONSENT_VALIDATION_OUTCOME")
        # When consent version mismatches, enforcer sets consent to None, leading to "No_Active_Consent" path.
        self.assertEqual(audit_kwargs.get("status"), "Transformed_Fallback_No_Active_Consent", f"Actual status: {audit_kwargs.get('status')}")


    def test_type_errors_in_constructor(self):
        with self.assertRaisesRegex(TypeError, "policy_store must be an instance of PolicyStore"):
            PrivacyEnforcer(None, self.mock_consent_manager, self.mock_data_classifier, self.mock_policy_evaluator, self.mock_obfuscation_engine)
        # ... similar checks for other constructor arguments can be added if desired ...
        with self.assertRaisesRegex(TypeError, "obfuscation_engine must be an instance of ObfuscationEngine"):
            PrivacyEnforcer(self.mock_policy_store, self.mock_consent_manager, self.mock_data_classifier, self.mock_policy_evaluator, None)


if __name__ == '__main__':
    # Need to define Optional for type hints if running standalone for some Python versions
    from typing import Optional
    unittest.main()
