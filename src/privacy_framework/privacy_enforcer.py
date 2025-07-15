from .data_classifier import DataClassifier
from .data_auditor import DataTransformationAuditor
from .consent_manager import ConsentManager
from .policy_store import PolicyStore
from .policy_evaluator import PolicyEvaluator
from .obfuscation_engine import ObfuscationEngine
from typing import Dict, Any, Optional

class PrivacyEnforcer:
    def __init__(self, policy_store: PolicyStore, consent_manager: ConsentManager, auditor: DataTransformationAuditor):
        self.policy_store = policy_store
        self.consent_manager = consent_manager
        self.auditor = auditor
        self.data_classifier = DataClassifier()
        self.policy_evaluator = PolicyEvaluator()
        self.obfuscation_engine = ObfuscationEngine()

    def process_data_stream(self, user_id: str, policy_id: str, data_record: Dict[str, Any], intended_purpose: str, intended_third_party: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a data stream according to the user's consent and the privacy policy.
        """
        policy = self.policy_store.load_policy(policy_id)
        consent = self.consent_manager.consent_store.load_latest_consent(user_id, policy_id)

        if not policy or not consent:
            return {"privacy_status": "Denied", **data_record}

        if not self.policy_evaluator.is_purpose_permitted(policy, consent, intended_purpose):
            return {"privacy_status": "Denied", **data_record}

        classified_data = self.data_classifier.classify(data_record)

        # For this demo, we assume that if the purpose is permitted, we can obfuscate sensitive data.
        # A more complex implementation would have more granular rules.
        obfuscated_data = self.obfuscation_engine.obfuscate_data(data_record, classified_data)

        self.auditor.log_event(
            event_type="data_processing",
            original_data=data_record,
            transformed_data=obfuscated_data,
            policy_id=policy_id,
            consent_id=consent.consent_id,
            outcome="Permitted_Obfuscated"
        )

        return {"privacy_status": "Permitted_Obfuscated", **obfuscated_data}
