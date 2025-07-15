import os
from privacy_framework.policy_store import PolicyStore
from privacy_framework.consent_store import ConsentStore
from privacy_framework.consent_manager import ConsentManager
from privacy_framework.privacy_policy import PrivacyPolicy
import datetime

def demonstrate_persistence():
    # Initialize stores
    policy_store = PolicyStore()
    consent_store = ConsentStore()
    consent_manager = ConsentManager(consent_store)

    # Create and save a policy
    policy = PrivacyPolicy(
        policy_id="user_data_policy",
        version=1,
        content="This policy governs the collection and use of user data.",
        rules=["Rule1", "Rule2"]
    )
    policy_store.save_policy(policy)
    print(f"Saved policy: {policy.policy_id} v{policy.version}")

    # Grant consent
    user_id = "user123"
    consent = consent_manager.grant_consent(user_id, policy.policy_id, policy.version)
    print(f"Granted consent for user {user_id} to policy {policy.policy_id}")

    # --- Simulate application restart ---
    print("\n--- Simulating application restart ---")
    del policy_store
    del consent_store
    del consent_manager

    # Re-initialize stores
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
    demonstrate_persistence()
