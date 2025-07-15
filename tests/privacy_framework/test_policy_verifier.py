import unittest
from src.privacy_framework.privacy_policy import PrivacyPolicy
from src.privacy_framework.policy_verifier import PrivacyPolicyVerifier

class TestPrivacyPolicyVerifier(unittest.TestCase):

    def test_verify_policy_success(self):
        policy = PrivacyPolicy(
            policy_id="test_policy",
            version=1,
            content="Test policy content",
            rules=["allow_marketing_data_collection", "allow_opt_out"]
        )
        self.assertTrue(PrivacyPolicyVerifier.verify_policy(policy, "user_can_opt_out_of_marketing"))

    def test_verify_policy_failure(self):
        policy = PrivacyPolicy(
            policy_id="test_policy",
            version=1,
            content="Test policy content",
            rules=["allow_marketing_data_collection"]
        )
        self.assertFalse(PrivacyPolicyVerifier.verify_policy(policy, "user_can_opt_out_of_marketing"))

if __name__ == '__main__':
    unittest.main()
