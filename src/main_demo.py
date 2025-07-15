import os
from privacy_framework.policy_store import PolicyStore
from privacy_framework.consent_store import ConsentStore
from privacy_framework.consent_manager import ConsentManager
from privacy_framework.privacy_policy import PrivacyPolicy
import datetime

from privacy_framework.data_auditor import DataTransformationAuditor
from privacy_framework.privacy_enforcer import PrivacyEnforcer
from privacy_framework.policy_verifier import PrivacyPolicyVerifier

def demonstrate_persistence_and_auditing():
    # Initialize stores and managers
    policy_store = PolicyStore()
    consent_store = ConsentStore()
    consent_manager = ConsentManager(consent_store)
    auditor = DataTransformationAuditor()
    enforcer = PrivacyEnforcer(policy_store, consent_manager, auditor)

    # Create and save a policy
    policy = PrivacyPolicy(
        policy_id="user_data_policy",
        version=1,
        content="This policy governs the collection and use of user data.",
        rules=["allow_marketing_data_collection", "allow_opt_out"]
    )
    policy_store.save_policy(policy)
    print(f"Saved policy: {policy.policy_id} v{policy.version}")

    # Verify a property of the policy
    PrivacyPolicyVerifier.verify_policy(policy, "user_can_opt_out_of_marketing")

    # Grant consent
    user_id = "user123"
    consent = consent_manager.grant_consent(user_id, policy.policy_id, policy.version)
    print(f"Granted consent for user {user_id} to policy {policy.policy_id}")

    # Process some data
    user_data = {"name": "John Doe", "email": "john.doe@example.com", "city": "New York"}
    print(f"\nOriginal data: {user_data}")
    processed_data = enforcer.process_data_stream(user_id, "user_data_policy", user_data, "Marketing")
    print(f"Processed data: {processed_data}")

    # --- Simulate application restart ---
    print("\n--- Simulating application restart ---")
    del policy_store
    del consent_store
    del consent_manager
    del auditor
    del enforcer

    # Re-initialize stores and managers
    policy_store = PolicyStore()
    consent_store = ConsentStore()
    consent_manager = ConsentManager(consent_store)

    # Load policy and check consent
    loaded_policy = policy_store.load_policy(policy.policy_id)
    if loaded_policy:
        print(f"Loaded policy: {loaded_policy.policy_id} v{loaded_policy.version}")
        has_consent = consent_manager.has_consent(user_id, loaded_policy.policy_id)
        print(f"User {user_id} has consent for policy {loaded_policy.policy_id}: {has_consent}")
    else:
        print(f"Could not load policy: {policy.policy_id}")


if __name__ == "__main__":
    demonstrate_persistence_and_auditing()
