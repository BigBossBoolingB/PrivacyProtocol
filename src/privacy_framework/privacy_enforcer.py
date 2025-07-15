from .data_classifier import DataClassifier
from .data_auditor import DataTransformationAuditor
from .consent_manager import ConsentManager
from .policy_store import PolicyStore

class PrivacyEnforcer:
    def __init__(self, policy_store: PolicyStore, consent_manager: ConsentManager, auditor: DataTransformationAuditor):
        self.policy_store = policy_store
        self.consent_manager = consent_manager
        self.auditor = auditor

    def process_data(self, user_id: str, data: dict) -> dict:
        """
        Processes data according to the user's consent and the privacy policy.
        """
        # For simplicity, we assume a single policy for this demonstration
        policy_id = "user_data_policy"
        policy = self.policy_store.load_policy(policy_id)

        if not policy:
            # No policy, no processing
            return data

        if not self.consent_manager.has_consent(user_id, policy_id):
            # No consent, no processing
            return data

        classified_data = DataClassifier.classify(data)
        transformed_data = data.copy()

        for key, classification in classified_data.items():
            if classification == "sensitive":
                # Obfuscate sensitive data
                transformed_data[key] = "********"

        self.auditor.log_event(
            event_type="data_processing",
            original_data=data,
            transformed_data=transformed_data,
            policy_id=policy_id,
            consent_id=f"consent_{user_id}_{policy_id}", # Simplified for demo
            outcome="success"
        )

        return transformed_data
