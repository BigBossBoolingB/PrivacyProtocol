from typing import Tuple, Dict, Any, Optional

try:
    from .policy import PrivacyPolicy, Purpose
    from .consent import UserConsent
    from .policy_store import PolicyStore
    from .consent_manager import ConsentManager
    from .data_classifier import DataClassifier
    from .policy_evaluator import PolicyEvaluator
    from .obfuscation_engine import ObfuscationEngine
except ImportError: # For standalone testing/mocking if needed
    # Define dummy classes if run standalone and imports fail,
    # though tests should use mocks.
    class PrivacyPolicy: pass
    class Purpose: pass
    class UserConsent: pass
    class PolicyStore: pass
    class ConsentManager: pass
    class DataClassifier: pass
    class PolicyEvaluator: pass
    class ObfuscationEngine: pass


class PrivacyEnforcer:
    def __init__(self,
                 policy_store: PolicyStore,
                 consent_manager: ConsentManager,
                 data_classifier: DataClassifier,
                 policy_evaluator: PolicyEvaluator,
                 obfuscation_engine: ObfuscationEngine):

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

        self.policy_store = policy_store
        self.consent_manager = consent_manager
        self.data_classifier = data_classifier
        self.policy_evaluator = policy_evaluator
        self.obfuscation_engine = obfuscation_engine

    def process_data_record(self,
                              user_id: str,
                              policy_id: str,
                              policy_version: Optional[str], # Specify version or None for latest
                              data_record: Dict[str, Any],
                              intended_purpose: Purpose,
                              intended_third_party: Optional[str] = None
                             ) -> Tuple[Dict[str, Any], str]:
        """
        Processes a data record according to the specified policy, user consent,
        and intended purpose, applying obfuscation if necessary.

        Args:
            user_id: The ID of the user associated with the data.
            policy_id: The ID of the governing privacy policy.
            policy_version: The specific version of the policy to use (or None for latest).
            data_record: The dictionary containing the raw data.
            intended_purpose: The Purpose enum for which the data is being processed.
            intended_third_party: Optional name of the third party if data is shared.

        Returns:
            A tuple containing:
                - The processed data record (possibly obfuscated).
                - A status string (e.g., "Allowed_Raw", "Allowed_Transformed",
                                   "Policy_Not_Found", "Consent_Not_Found_Or_Inactive").
        """

        # 1. Load Policy
        policy = self.policy_store.load_policy(policy_id, version=policy_version)
        if not policy:
            return data_record, "Policy_Not_Found" # Return original data if policy missing

        # 2. Get Active Consent
        # If no policy_version was specified for loading, use the version from the loaded (latest) policy
        # for consent matching, assuming consent is tied to a specific policy version.
        effective_policy_version = policy.version
        consent = self.consent_manager.get_active_consent(user_id, policy_id)

        # Further check if the active consent matches the effective policy version.
        # This logic might need refinement based on how strictly consent is version-locked.
        # For now, if an active consent exists for the policy_id, we use it, assuming
        # the ConsentManager's get_active_consent handles version compatibility or returns the most relevant.
        # A stricter check:
        if consent and consent.policy_version != effective_policy_version:
            # This case means active consent is for a *different version* of the same policy_id.
            # Depending on rules, this might be invalid, or some mapping/migration logic could apply.
            # For now, treat as if consent for *this specific version* is not found or is not the one active.
             # print(f"Warning: Active consent version {consent.policy_version} does not match effective policy version {effective_policy_version}")
             # To be strict, we might set consent to None here if versions must match exactly.
             # For simplicity, if any active consent for policy_id is found, we proceed,
             # but PolicyEvaluator will use the consent's own policy_version for its checks if needed.
             # However, the PolicyEvaluator is given the loaded `policy` object.
             pass # Current ConsentManager's get_active_consent doesn't filter by policy_version string, just policy_id.

        if not consent or not consent.is_active: # is_active check is also in ConsentManager.get_active_consent
            # If no active consent, the ObfuscationEngine will likely obfuscate everything
            # by default as PolicyEvaluator will get consent=None.
            # We can set a specific status here.
            processed_data_no_consent = self.obfuscation_engine.process_data_for_operation(
                raw_data=data_record,
                policy=policy,
                consent=None, # Explicitly pass None
                proposed_purpose=intended_purpose,
                data_classifier=self.data_classifier,
                policy_evaluator=self.policy_evaluator,
                proposed_third_party=intended_third_party
            )
            # If all fields are identical, it means policy allowed raw without consent (e.g. legal obligation)
            # This part of PolicyEvaluator is not yet fully implemented.
            # For now, assume if no active consent, it's transformed/denied based on default obfuscation.
            is_identical_no_consent = all(
                processed_data_no_consent.get(k) == v for k, v in data_record.items()
            ) and all(k in data_record for k in processed_data_no_consent)

            if is_identical_no_consent:
                 return processed_data_no_consent, "Allowed_Raw_By_Policy_No_Active_Consent" # Or a more specific status
            return processed_data_no_consent, "Transformed_Due_To_No_Active_Consent"


        # 3. Process data using ObfuscationEngine (which uses Classifier and Evaluator)
        processed_data = self.obfuscation_engine.process_data_for_operation(
            raw_data=data_record,
            policy=policy,
            consent=consent,
            proposed_purpose=intended_purpose,
            data_classifier=self.data_classifier,
            policy_evaluator=self.policy_evaluator,
            proposed_third_party=intended_third_party
        )

        # 4. Determine overall status
        # Compare processed_data with data_record to see if any obfuscation occurred.
        # This is a simplified check. A more robust status could come from PolicyEvaluator
        # or ObfuscationEngine indicating *why* transformations happened.
        is_identical = all(
            processed_data.get(k) == v for k, v in data_record.items()
        ) and all(k in data_record for k in processed_data) # ensure same keys too

        if is_identical:
            status = "Allowed_Raw"
        else:
            status = "Allowed_Transformed"
            # Future: Could refine status to "Partially_Allowed_Raw_Partially_Transformed"
            # Or "Denied_Some_Fields_Transformed_Others" if some fields were completely blocked
            # (current ObfuscationEngine doesn't block, only transforms or passes raw).

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
    #
    # ps = PolicyStore("./_temp_enforcer_policies")
    # cs = ConsentStore("./_temp_enforcer_consents")
    # cm = ConsentManager(cs)
    # dc = DataClassifier()
    # pe = PolicyEvaluator()
    # oe = ObfuscationEngine()
    #
    # enforcer = PrivacyEnforcer(ps, cm, dc, pe, oe)
    # print(f"PrivacyEnforcer instance created: {enforcer}")
    pass
