# src/privacy_framework/privacy_enforcer.py
"""
Service to enforce privacy policies on data streams.
"""
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum

try:
    from .data_classifier import DataClassifier
    from .policy_evaluator import PolicyEvaluator
    from .obfuscation_engine import ObfuscationEngine
    from .consent_manager import ConsentManager
    from .policy_store import PolicyStore
    from .policy import PrivacyPolicy, Purpose, LegalBasis
    from .consent import UserConsent
    from .data_attribute import DataAttribute, ObfuscationMethod # Added ObfuscationMethod for fallback
except ImportError:
    # Fallback for direct execution or different project structures
    from privacy_framework.data_classifier import DataClassifier
    from privacy_framework.policy_evaluator import PolicyEvaluator
    from privacy_framework.obfuscation_engine import ObfuscationEngine
    from privacy_framework.consent_manager import ConsentManager
    from privacy_framework.policy_store import PolicyStore
    from privacy_framework.policy import PrivacyPolicy, Purpose, LegalBasis
    from privacy_framework.consent import UserConsent
    from privacy_framework.data_attribute import DataAttribute, ObfuscationMethod # Added ObfuscationMethod for fallback


class PrivacyStatus(Enum):
    """Indicates the outcome of privacy enforcement on a data record."""
    PERMITTED_RAW = "Permitted_Raw"
    PERMITTED_OBFUSCATED = "Permitted_Obfuscated"
    DENIED_NO_POLICY = "Denied_NoPolicy"
    DENIED_NO_CONSENT = "Denied_NoConsent" # When consent is required but missing/inactive
    DENIED_POLICY_RESTRICTION = "Denied_PolicyRestriction" # Policy itself forbids (e.g. purpose)
    DENIED_CONSENT_RESTRICTION = "Denied_ConsentRestriction" # Consent forbids (e.g. category/purpose)
    ERROR_PROCESSING = "Error_Processing"


class PrivacyEnforcer:
    """
    Central service for applying the Privacy Protocol to incoming data.
    It orchestrates classification, policy/consent evaluation, and obfuscation.
    """

    def __init__(self,
                 data_classifier: DataClassifier,
                 policy_evaluator: PolicyEvaluator,
                 obfuscation_engine: ObfuscationEngine,
                 consent_manager: ConsentManager,
                 policy_store: PolicyStore,
                 auditor: Optional['DataTransformationAuditor'] = None,
                 policy_verifier: Optional['PolicyVerifier'] = None): # Added policy_verifier
        self.data_classifier = data_classifier
        self.policy_evaluator = policy_evaluator
        self.obfuscation_engine = obfuscation_engine
        self.consent_manager = consent_manager
        self.policy_store = policy_store
        self.auditor = auditor
        self.policy_verifier = policy_verifier # Added policy_verifier

    def process_data_record(self,
                              user_id: str,
                              policy_id: str,
                              policy_version: Optional[int], # Policy version is crucial
                              data_record: Dict[str, Any],
                              intended_purpose: Purpose,
                              intended_third_party: Optional[str] = None
                             ) -> Dict[str, Any]:
        """
        Processes a single data record according to a specific policy and user consent.

        Returns a dictionary containing:
            - 'status': PrivacyStatus enum member
            - 'processed_data': The data record (original, obfuscated, or None if fully denied)
            - 'message': A string explaining the outcome.
        """
        # 1. Load the relevant PrivacyPolicy
        policy = self.policy_store.load_policy(policy_id, version=policy_version)

        if not policy: # DENIED_NO_POLICY case
            classified_attrs_fallback = self.data_classifier.classify_data(data_record)
            # Perform a default strict obfuscation for all fields
            processed_fallback = {
                key: self.obfuscation_engine.obfuscate_field(
                    value,
                    # Try to get preferred method, else REDACT
                    next((attr.obfuscation_method_preferred for attr in classified_attrs_fallback if attr.attribute_name == key and attr.obfuscation_method_preferred != ObfuscationMethod.NONE), ObfuscationMethod.REDACT)
                ) for key, value in data_record.items()
            }
            if self.auditor:
                self.auditor.log_event(
                    event_type=PrivacyStatus.DENIED_NO_POLICY.name,
                    details={"user_id": user_id, "attempted_policy_id": policy_id, "attempted_version": policy_version,
                             "intended_purpose": intended_purpose.name, "intended_third_party": intended_third_party,
                             "reason": "Policy not found."},
                    original_data=data_record, processed_data=processed_fallback, policy_id=policy_id)
            return {"status": PrivacyStatus.DENIED_NO_POLICY, "processed_data": processed_fallback,
                    "message": f"Policy {policy_id} v{policy_version or 'latest'} not found. Data fully obfuscated by default."}

        # 1.5 Conceptual: Verify policy adherence to formal rules *before* operational checks
        if self.policy_verifier:
            # Note: verify_policy_adherence currently only checks policy structure.
            # A more advanced verifier might take `intended_purpose`, `data_record` (or its classification)
            # to check operational rules against the policy.
            # For now, we check general policy soundness.
            verification_results = self.policy_verifier.verify_policy_adherence(policy)
            failed_rules = [rule_id for rule_id, adhered in verification_results.items() if not adhered]
            if failed_rules:
                # Policy itself is flawed according to formal rules. Deny and obfuscate all.
                classified_attrs_fallback = self.data_classifier.classify_data(data_record)
                processed_fallback = {
                    key: self.obfuscation_engine.obfuscate_field(
                        value,
                        next((attr.obfuscation_method_preferred for attr in classified_attrs_fallback if attr.attribute_name == key and attr.obfuscation_method_preferred != ObfuscationMethod.NONE), ObfuscationMethod.REDACT)
                    ) for key, value in data_record.items()
                }
                if self.auditor:
                    self.auditor.log_event(
                        event_type=PrivacyStatus.DENIED_POLICY_RESTRICTION.name,
                        details={"user_id": user_id, "policy_id": policy.policy_id, "policy_version": policy.version,
                                 "intended_purpose": intended_purpose.name, "intended_third_party": intended_third_party,
                                 "reason": f"Policy failed formal verification for rules: {', '.join(failed_rules)}."},
                        original_data=data_record, processed_data=processed_fallback, policy_id=policy.policy_id)
                return {"status": PrivacyStatus.DENIED_POLICY_RESTRICTION, "processed_data": processed_fallback,
                        "message": f"Policy {policy.policy_id} failed formal verification. Operation denied. Violated rules: {', '.join(failed_rules)}."}

        # 2. Load UserConsent for the user and policy
        # ConsentManager's get_active_consent should ideally check policy version match too.
        # For now, we assume it gets the active one for the policy_id, and evaluator checks version.
        user_consent = self.consent_manager.get_active_consent(user_id, policy_id)

        if policy.legal_basis == LegalBasis.CONSENT and not user_consent:
             # Classify to know preferred obfuscation methods even if denying
            classified_attributes = self.data_classifier.classify_data(data_record)
            obfuscated_data = {}
            for attr in classified_attributes:
                original_value = data_record.get(attr.attribute_name) # Assuming flat dict for now
                # If key is nested, data_record.get() won't work directly with flattened attr.attribute_name
                # This part needs careful handling for nested data if keys in data_record don't match attr.attribute_name
                # For this V1, assume data_record is flat and keys match attr.attribute_name from classifier.
                if attr.attribute_name in data_record:
                     obfuscated_data[attr.attribute_name] = self.obfuscation_engine.obfuscate_field(
                        original_value, attr.obfuscation_method_preferred
                    )
                else: # Should not happen if classifier works on data_record keys
                    obfuscated_data[attr.attribute_name] = "[CLASSIFICATION_KEY_MISMATCH]"

            if self.auditor:
                self.auditor.log_event(
                    event_type=PrivacyStatus.DENIED_NO_CONSENT.name,
                    details={
                        "user_id": user_id, "policy_id": policy_id, "policy_version": policy_version,
                        "intended_purpose": intended_purpose.name, "intended_third_party": intended_third_party,
                        "reason": "Consent required by policy but no active consent found."
                    },
                    original_data=data_record,
                    processed_data=obfuscated_data,
                    policy_id=policy_id,
                    consent_id=None
                )
            return {
                "status": PrivacyStatus.DENIED_NO_CONSENT,
                "processed_data": obfuscated_data,
                "message": f"Active consent required for policy {policy_id} but not found for user {user_id}. Data obfuscated according to attribute preferences." # Updated message
            }

        # 3. Classify the incoming data_record
        classified_attributes: List[DataAttribute] = self.data_classifier.classify_data(data_record)
        if self.auditor:
            # Log data classification event
            self.auditor.log_event(
                event_type="DATA_CLASSIFICATION_ATTEMPTED", # More generic than "SUCCESSFUL" as it's just an attempt
                details={
                    "user_id": user_id, "policy_id": policy_id, "num_fields_in_record": len(data_record),
                    "num_attributes_classified": len(classified_attributes),
                    # Storing all classified attributes could be verbose; consider summarizing or hashing if needed
                    "attributes_summary": [{attr.attribute_name: attr.category.name} for attr in classified_attributes]
                },
                original_data=data_record,
                policy_id=policy_id,
                consent_id=user_consent.consent_id if user_consent else None
            )

        # 4. Use ObfuscationEngine to process data (which internally uses PolicyEvaluator)
        # The ObfuscationEngine's process_data_attributes will apply obfuscation field by field
        # based on whether the PolicyEvaluator permits the operation for that field.
        processed_data = self.obfuscation_engine.process_data_attributes(
            raw_data=data_record,
            classified_attributes=classified_attributes,
            policy=policy,
            consent=user_consent, # May be None if legal_basis is not CONSENT
            proposed_purpose=intended_purpose,
            policy_evaluator=self.policy_evaluator,
            proposed_third_party=intended_third_party
        )

        # 5. Determine overall status
        # This is a simplification. A more nuanced status might look at individual fields.
        # If any field was changed, it's PERMITTED_OBFUSCATED.
        # If no field was changed, it's PERMITTED_RAW.
        # This requires comparing processed_data with data_record.
        status = PrivacyStatus.PERMITTED_RAW
        if processed_data != data_record: # Simple check, might need deep comparison for complex objects
            status = PrivacyStatus.PERMITTED_OBFUSCATED
            # Check if all fields were redacted (or equivalent of full denial)
            # This logic can be more sophisticated
            all_denied = True
            for key, value in processed_data.items():
                # A bit heuristic: if it's redacted or a placeholder, consider it denied in raw form.
                if value != data_record.get(key) and not (isinstance(value, str) and ("[REDACTED]" in value or "[AGGREGATED" in value)):
                    all_denied = False # Some data might have passed through, or obfuscated differently
                    break
            if all_denied and any(processed_data.get(k) != data_record.get(k) for k in data_record):
                 # This means policy/consent restricted everything for this purpose
                 # The status would be set by PolicyEvaluator implicitly through ObfuscationEngine
                 # For now, let's assume ObfuscationEngine's output reflects the most granular outcome.
                 # The PrivacyStatus here is more about the overall record.
                 # A more specific DENIED status might be better if all_denied is true.
                 # For example, if status is PERMITTED_OBFUSCATED but all_denied is true,
                 # it implies every field was obfuscated to a point of denial.
                 # However, the current ObfuscationEngine.process_data_attributes aims to return usable (even if obfuscated) data.
                 # True "denial" of a field usually means it's fully redacted or removed.
                 # If status is PERMITTED_OBFUSCATED and all_denied is true, it's effectively a DENIED_CONSENT_RESTRICTION or DENIED_POLICY_RESTRICTION
                 # This logic can be refined here or within the ObfuscationEngine/PolicyEvaluator for more precise status reporting.
                 pass

        # Log the final processing event
        if self.auditor:
            self.auditor.log_event(
                event_type=status.name, # Use the determined status as the event type
                details={
                    "user_id": user_id, "policy_id": policy_id, "policy_version": policy_version,
                    "intended_purpose": intended_purpose.name,
                    "intended_third_party": intended_third_party,
                    "message": f"Final processing status: {status.name}"
                },
                original_data=data_record,
                processed_data=processed_data,
                policy_id=policy_id,
                consent_id=user_consent.consent_id if user_consent else None
            )

        return {
            "status": status,
            "processed_data": processed_data,
            "message": f"Data processed for user {user_id}, policy {policy_id}, purpose {intended_purpose.name}."
        }


if __name__ == '__main__':
    # This example requires setting up all dependent components with proper storage.
    # It's better demonstrated in main_demo.py which handles the setup.
    print("PrivacyEnforcer created. Run main_demo.py for a full demonstration.")

    # Conceptual minimal setup for a very basic manual test (won't run standalone without files)
    # from privacy_framework.consent_store import ConsentStore
    # policy_store = PolicyStore("_app_data_demo/policies_enforcer_test/")
    # consent_store = ConsentStore("_app_data_demo/consents_enforcer_test/")
    # consent_manager = ConsentManager(consent_store)
    # data_classifier = DataClassifier()
    # policy_evaluator = PolicyEvaluator()
    # obfuscation_engine = ObfuscationEngine()

    # enforcer = PrivacyEnforcer(
    #     data_classifier, policy_evaluator, obfuscation_engine, consent_manager, policy_store
    # )
    # print("Conceptual PrivacyEnforcer instance created (requires actual stores and data for real use).")
    pass
