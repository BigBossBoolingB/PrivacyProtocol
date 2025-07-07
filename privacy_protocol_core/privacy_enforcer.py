from __future__ import annotations # For string literal type hints
from typing import Tuple, Dict, Any, Optional

# Attempt to import DataTransformationAuditor first and define dummy if needed
try:
    from .auditing.data_auditor import DataTransformationAuditor
except ImportError:
    class DataTransformationAuditor: # Dummy for standalone if auditing module not found
        @staticmethod
        def hash_data(data): return "mock_hash_from_enforcer_dummy_auditor"
        def log_event(self, *args, **kwargs): pass

try:
    from .policy import PrivacyPolicy, Purpose
    from .consent import UserConsent
    from .policy_store import PolicyStore
    from .consent_manager import ConsentManager
    from .data_classifier import DataClassifier
    from .policy_evaluator import PolicyEvaluator
    from .obfuscation_engine import ObfuscationEngine
except ImportError: # For standalone testing/mocking if needed
    # Define other dummy classes if run standalone and imports fail
    class PrivacyPolicy: pass
    class Purpose: pass
    class UserConsent: pass
    class PolicyStore: pass
    class ConsentManager: pass
    class DataClassifier: pass
    class PolicyEvaluator: pass
    class ObfuscationEngine: pass
    # DataTransformationAuditor already attempted above


class PrivacyEnforcer:
    def __init__(self,
                 policy_store: PolicyStore,
                 consent_manager: ConsentManager,
                 data_classifier: DataClassifier,
                 policy_evaluator: PolicyEvaluator,
                 obfuscation_engine: ObfuscationEngine,
                 auditor: Optional['DataTransformationAuditor'] = None): # String literal hint

        if not isinstance(policy_store, PolicyStore):
            raise TypeError("policy_store must be an instance of PolicyStore.")
        if not isinstance(consent_manager, ConsentManager):
            raise TypeError("consent_manager must be an instance of ConsentManager.")
        if not isinstance(data_classifier, DataClassifier):
            raise TypeError("data_classifier must be an instance of DataClassifier.")
        if not isinstance(policy_evaluator, PolicyEvaluator):
            raise TypeError("policy_evaluator must be an instance of PolicyEvaluator.")
        if not isinstance(obfuscation_engine, ObfuscationEngine):
            raise TypeError("obfuscation_engine must be an instance of ObfuscationEngine.")
        if auditor is not None and not isinstance(auditor, DataTransformationAuditor):
            raise TypeError("auditor must be an instance of DataTransformationAuditor or None.")

        self.policy_store = policy_store
        self.consent_manager = consent_manager
        self.data_classifier = data_classifier
        self.policy_evaluator = policy_evaluator
        self.obfuscation_engine = obfuscation_engine
        self.auditor = auditor

    def _determine_transformation_details(self, raw_data: Dict[str, Any], processed_data: Dict[str, Any]) -> Dict[str, Any]:
        details = {"fields_changed": [], "fields_raw": []}
        all_keys = set(raw_data.keys()) | set(processed_data.keys())
        for key in all_keys:
            raw_value = raw_data.get(key)
            processed_value = processed_data.get(key)
            if raw_value != processed_value:
                details["fields_changed"].append(key)
            elif key in raw_data and key in processed_data : # Present in both and unchanged
                details["fields_raw"].append(key)
        return details

    def process_data_record(self,
                              user_id: str,
                              policy_id: str,
                              policy_version: Optional[str],
                              data_record: Dict[str, Any],
                              intended_purpose: Purpose,
                              intended_third_party: Optional[str] = None
                             ) -> Tuple[Dict[str, Any], str]:

        input_data_hash = self.auditor.hash_data(data_record) if self.auditor else "no_audit_input_hash"
        processed_data = data_record
        status = "Error_Processing_Failed"
        consent_id_for_audit: Optional[str] = None
        effective_policy_version_for_audit = str(policy_version) if policy_version else "latest"


        policy = self.policy_store.load_policy(policy_id, version=policy_version)
        if not policy:
            status = "Policy_Not_Found"
            if self.auditor:
                self.auditor.log_event(
                    event_type="POLICY_ACCESS_FAILURE", user_id=user_id, policy_id=policy_id,
                    policy_version=effective_policy_version_for_audit, consent_id=None,
                    input_data_hash=input_data_hash, output_data_hash=input_data_hash,
                    transformation_details={"error": "Policy not found at specified version or latest."}, status=status
                )
            return processed_data, status

        effective_policy_version_for_audit = policy.version # Use actual loaded policy version for audit

        consent = self.consent_manager.get_active_consent(user_id, policy_id)
        if consent:
            consent_id_for_audit = consent.consent_id

        # Strict consent version check: if consent's policy version doesn't match loaded policy version
        if consent and consent.policy_version != policy.version:
            # print(f"Warning: Active consent version {consent.policy_version} does not match effective policy version {policy.version}. Invalidating consent for this operation.")
            consent = None # Invalidate consent for this operation due to version mismatch

        if not consent or not consent.is_active:
            processed_data = self.obfuscation_engine.process_data_for_operation(
                raw_data=data_record, policy=policy, consent=None,
                proposed_purpose=intended_purpose, data_classifier=self.data_classifier,
                policy_evaluator=self.policy_evaluator, proposed_third_party=intended_third_party
            )
            status_reason = "No_Active_Consent" if not consent else "Consent_Inactive_Or_Version_Mismatch"

            is_identical_no_consent = all(
                processed_data.get(k) == v for k, v in data_record.items()
            ) and all(k in data_record for k in processed_data)

            if is_identical_no_consent:
                 status = f"Allowed_Raw_Fallback_{status_reason}" # Policy might allow raw on other basis
            else:
                status = f"Transformed_Fallback_{status_reason}"

            if self.auditor:
                output_data_hash = self.auditor.hash_data(processed_data)
                transform_details = self._determine_transformation_details(data_record, processed_data)
                self.auditor.log_event(
                    event_type="CONSENT_VALIDATION_OUTCOME", user_id=user_id, policy_id=policy.policy_id,
                    policy_version=policy.version, consent_id=consent_id_for_audit,
                    input_data_hash=input_data_hash, output_data_hash=output_data_hash,
                    transformation_details=transform_details, status=status
                )
            return processed_data, status

        # If active consent is present and matches policy version (implicitly or explicitly)
        processed_data = self.obfuscation_engine.process_data_for_operation(
            raw_data=data_record, policy=policy, consent=consent,
            proposed_purpose=intended_purpose, data_classifier=self.data_classifier,
            policy_evaluator=self.policy_evaluator, proposed_third_party=intended_third_party
        )

        is_identical = all(
            processed_data.get(k) == v for k, v in data_record.items()
        ) and all(k in data_record for k in processed_data)

        if is_identical:
            status = "Allowed_Raw_With_Consent"
        else:
            status = "Allowed_Transformed_With_Consent"

        if self.auditor:
            output_data_hash = self.auditor.hash_data(processed_data)
            transform_details = self._determine_transformation_details(data_record, processed_data)
            self.auditor.log_event(
                event_type="DATA_PROCESSED_WITH_VALID_CONSENT", user_id=user_id, policy_id=policy.policy_id,
                policy_version=policy.version, consent_id=consent.consent_id,
                input_data_hash=input_data_hash, output_data_hash=output_data_hash,
                transformation_details=transform_details, status=status
            )

        return processed_data, status


if __name__ == '__main__':
    # This block requires full setup of all dependent components (stores, managers, etc.)
    # and is better demonstrated in the main.py of the application,
    # or with comprehensive mocks in unit tests.
    print("PrivacyEnforcer conceptualized. Run main.py for an end-to-end demonstration or unit tests for isolated testing.")
    print("Example of direct instantiation (requires mock/real dependencies):")
    # from policy_store import PolicyStore
    # from consent_manager import ConsentManager
    # from consent_store import ConsentStore
    # from data_classifier import DataClassifier
    # from policy_evaluator import PolicyEvaluator
    # from obfuscation_engine import ObfuscationEngine
    # from auditing.data_auditor import DataTransformationAuditor # Corrected import path
    #
    # ps = PolicyStore("./_temp_enforcer_policies")
    # cs = ConsentStore("./_temp_enforcer_consents")
    # cm = ConsentManager(cs)
    # dc = DataClassifier()
    # pe = PolicyEvaluator()
    # oe = ObfuscationEngine()
    # da = DataTransformationAuditor("./_temp_enforcer_audit_logs")
    #
    # enforcer = PrivacyEnforcer(ps, cm, dc, pe, oe, da)
    # print(f"PrivacyEnforcer instance created: {enforcer}")
    pass
