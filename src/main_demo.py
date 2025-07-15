import os
from privacy_framework.policy_store import PolicyStore
from privacy_framework.consent_store import ConsentStore
from privacy_framework.consent_manager import ConsentManager
from privacy_framework.privacy_policy import PrivacyPolicy
import datetime

from privacy_framework.data_auditor import DataTransformationAuditor
from privacy_framework.privacy_enforcer import PrivacyEnforcer
from demo_helpers.mock_data_generator import MockDataGenerator

def end_to_end_demo():
    # 1. Initialize all core components
    policy_store = PolicyStore()
    consent_store = ConsentStore()
    consent_manager = ConsentManager(consent_store)
    auditor = DataTransformationAuditor()
    enforcer = PrivacyEnforcer(policy_store, consent_manager, auditor)

    # 2. Define and Save Sample PrivacyPolicy
    gdpr_like_policy = PrivacyPolicy(
        policy_id="gdpr_like_policy",
        version=1,
        content="A policy that allows analytics but not marketing.",
        rules=["allow_analytics"]
    )
    policy_store.save_policy(gdpr_like_policy)
    print(f"Saved policy: {gdpr_like_policy.policy_id}")

    # 3. Simulate User Consent
    consent_manager.grant_consent("user_a", "gdpr_like_policy", 1)
    print("User A has granted consent to the GDPR-like policy.")

    # 4. Generate & Process Data Stream
    print("\n--- Processing Data Stream ---")
    for _ in range(3):
        data_record = MockDataGenerator.generate_user_activity_record()
        user_id = data_record["user_id"]

        print(f"\nOriginal data for {user_id}: {data_record}")

        # Attempt to process for Analytics
        processed_for_analytics = enforcer.process_data_stream(
            user_id=user_id,
            policy_id="gdpr_like_policy",
            data_record=data_record,
            intended_purpose="Analytics"
        )
        print(f"Processed for Analytics: {processed_for_analytics}")

        # Attempt to process for Marketing
        processed_for_marketing = enforcer.process_data_stream(
            user_id=user_id,
            policy_id="gdpr_like_policy",
            data_record=data_record,
            intended_purpose="Marketing"
        )
        print(f"Processed for Marketing: {processed_for_marketing}")

    # 7. Show Audit Log
    print("\n--- Audit Log ---")
    with open(auditor.log_file_path, "r") as f:
        for line in f.readlines():
            print(line.strip())

if __name__ == "__main__":
    end_to_end_demo()
