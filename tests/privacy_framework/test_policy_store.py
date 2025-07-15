import os
import shutil
import unittest
from src.privacy_framework.policy_store import PolicyStore
from src.privacy_framework.privacy_policy import PrivacyPolicy

class TestPolicyStore(unittest.TestCase):

    def setUp(self):
        self.storage_path = "_test_policies/"
        self.policy_store = PolicyStore(storage_path=self.storage_path)
        self.policy = PrivacyPolicy(
            policy_id="test_policy",
            version=1,
            content="Test policy content",
            rules=["Rule1"]
        )

    def tearDown(self):
        if os.path.exists(self.storage_path):
            shutil.rmtree(self.storage_path)

    def test_save_and_load_policy(self):
        self.policy_store.save_policy(self.policy)
        loaded_policy = self.policy_store.load_policy(self.policy.policy_id, self.policy.version)
        self.assertEqual(self.policy, loaded_policy)

    def test_load_latest_policy(self):
        policy_v1 = self.policy
        policy_v2 = PrivacyPolicy(
            policy_id="test_policy",
            version=2,
            content="Test policy content v2",
            rules=["Rule1", "Rule2"]
        )
        self.policy_store.save_policy(policy_v1)
        self.policy_store.save_policy(policy_v2)
        latest_policy = self.policy_store.load_policy(self.policy.policy_id)
        self.assertEqual(policy_v2, latest_policy)

    def test_get_all_policies(self):
        self.policy_store.save_policy(self.policy)
        all_policies = self.policy_store.get_all_policies()
        self.assertEqual(1, len(all_policies))
        self.assertEqual(self.policy, all_policies[0])

    def test_load_non_existent_policy(self):
        loaded_policy = self.policy_store.load_policy("non_existent_policy")
        self.assertIsNone(loaded_policy)

if __name__ == '__main__':
    unittest.main()
