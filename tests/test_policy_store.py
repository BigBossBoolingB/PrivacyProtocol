# tests/test_policy_store.py
import unittest
import os
import shutil
import json
import time

# Adjust import path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis
from src.privacy_framework.policy_store import PolicyStore

class TestPolicyStore(unittest.TestCase):
    TEST_STORAGE_PATH = "_app_data_test/test_policies/"
    policy_id_1 = "policy_store_test_001"
    policy_id_2 = "policy_store_test_002"

    def setUp(self):
        """Set up a clean storage directory for each test."""
        if os.path.exists(self.TEST_STORAGE_PATH):
            shutil.rmtree(self.TEST_STORAGE_PATH)
        # os.makedirs(self.TEST_STORAGE_PATH) # Store constructor will make it
        self.policy_store = PolicyStore(storage_path=self.TEST_STORAGE_PATH)

        self.policy1_v1_data = {
            "policy_id": self.policy_id_1, "version": 1,
            "data_categories": [DataCategory.PERSONAL_INFO.value],
            "purposes": [Purpose.SERVICE_DELIVERY.value],
            "retention_period": "1 year", "third_parties_shared_with": [],
            "legal_basis": LegalBasis.CONSENT.value, "text_summary": "Policy 1, Version 1",
            "timestamp": int(time.time()) - 100
        }
        self.policy1_v1 = PrivacyPolicy.from_dict(self.policy1_v1_data)

        self.policy1_v2_data = {
            "policy_id": self.policy_id_1, "version": 2,
            "data_categories": [DataCategory.PERSONAL_INFO.value, DataCategory.USAGE_DATA.value],
            "purposes": [Purpose.SERVICE_DELIVERY.value, Purpose.ANALYTICS.value],
            "retention_period": "2 years", "third_parties_shared_with": ["analytics.partner.com"],
            "legal_basis": LegalBasis.CONSENT.value, "text_summary": "Policy 1, Version 2 (updated)",
            "timestamp": int(time.time()) - 50
        }
        self.policy1_v2 = PrivacyPolicy.from_dict(self.policy1_v2_data)

        self.policy2_v1_data = {
            "policy_id": self.policy_id_2, "version": 1,
            "data_categories": [DataCategory.DEVICE_INFO.value], "purposes": [Purpose.SECURITY.value],
            "retention_period": "30 days", "third_parties_shared_with": [],
            "legal_basis": LegalBasis.LEGITIMATE_INTERESTS.value, "text_summary": "Policy 2, Version 1",
            "timestamp": int(time.time()) - 200
        }
        self.policy2_v1 = PrivacyPolicy.from_dict(self.policy2_v1_data)


    def tearDown(self):
        """Clean up the storage directory after each test."""
        if os.path.exists(self.TEST_STORAGE_PATH):
            shutil.rmtree(self.TEST_STORAGE_PATH)

    def test_directory_creation(self):
        """Test if the storage directory is created by constructor."""
        path = "_app_data_test/new_policy_dir/"
        if os.path.exists(path): shutil.rmtree(path)
        self.assertFalse(os.path.exists(path))
        PolicyStore(storage_path=path)
        self.assertTrue(os.path.exists(path))
        shutil.rmtree(path)

    def test_save_policy(self):
        self.assertTrue(self.policy_store.save_policy(self.policy1_v1))
        expected_path = os.path.join(self.TEST_STORAGE_PATH, f"{self.policy1_v1.policy_id}_v{self.policy1_v1.version}.json")
        self.assertTrue(os.path.exists(expected_path))

        with open(expected_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data["policy_id"], self.policy1_v1.policy_id)
        self.assertEqual(data["version"], self.policy1_v1.version)

    def test_load_specific_version(self):
        self.policy_store.save_policy(self.policy1_v1)
        self.policy_store.save_policy(self.policy1_v2)

        loaded_v1 = self.policy_store.load_policy(self.policy_id_1, version=1)
        self.assertIsNotNone(loaded_v1)
        self.assertEqual(loaded_v1.version, 1)
        self.assertEqual(loaded_v1.text_summary, "Policy 1, Version 1")

        loaded_v2 = self.policy_store.load_policy(self.policy_id_1, version=2)
        self.assertIsNotNone(loaded_v2)
        self.assertEqual(loaded_v2.version, 2)
        self.assertEqual(loaded_v2.text_summary, "Policy 1, Version 2 (updated)")

    def test_load_latest_version(self):
        self.policy_store.save_policy(self.policy1_v1)
        time.sleep(0.01) # ensure v2 is slightly later if timestamps were identical
        self.policy_store.save_policy(self.policy1_v2)

        latest = self.policy_store.load_policy(self.policy_id_1) # version=None
        self.assertIsNotNone(latest)
        self.assertEqual(latest.version, 2)
        self.assertEqual(latest.text_summary, "Policy 1, Version 2 (updated)")

    def test_load_policy_non_existent_id(self):
        self.assertIsNone(self.policy_store.load_policy("non_existent_id"))

    def test_load_policy_non_existent_version(self):
        self.policy_store.save_policy(self.policy1_v1)
        self.assertIsNone(self.policy_store.load_policy(self.policy_id_1, version=3))

    def test_get_all_policies_loads_latest_versions(self):
        self.policy_store.save_policy(self.policy1_v1)
        self.policy_store.save_policy(self.policy1_v2) # p1v2 is latest for policy_id_1
        self.policy_store.save_policy(self.policy2_v1) # p2v1 is only and latest for policy_id_2

        all_policies = self.policy_store.get_all_policies()
        self.assertEqual(len(all_policies), 2)

        ids_and_versions = sorted([(p.policy_id, p.version) for p in all_policies])
        expected_ids_and_versions = sorted([
            (self.policy_id_1, 2), # Latest for policy1
            (self.policy_id_2, 1)  # Latest for policy2
        ])
        self.assertEqual(ids_and_versions, expected_ids_and_versions)

    def test_get_all_policies_empty_store(self):
        all_policies = self.policy_store.get_all_policies()
        self.assertEqual(len(all_policies), 0)

    def test_persistence_across_instances(self):
        self.policy_store.save_policy(self.policy1_v1)

        # Create a new store instance pointing to the same path
        new_store = PolicyStore(storage_path=self.TEST_STORAGE_PATH)
        loaded_policy = new_store.load_policy(self.policy_id_1, version=1)
        self.assertIsNotNone(loaded_policy)
        self.assertEqual(loaded_policy.policy_id, self.policy1_v1.policy_id)
        self.assertEqual(loaded_policy.version, self.policy1_v1.version)

    def test_handle_invalid_json_file(self):
        # Create a corrupted JSON file
        filepath = self.policy_store._get_policy_filepath("corrupted_policy", 1)
        with open(filepath, 'w') as f:
            f.write("{'invalid_json': True,") # Missing closing brace, single quotes

        loaded = self.policy_store.load_policy("corrupted_policy", 1)
        self.assertIsNone(loaded) # Should fail to load and return None

    def test_handle_malformed_policy_data(self):
        # JSON is valid, but data is missing required fields for PrivacyPolicy
        malformed_data = {"policy_id": "malformed", "version": 1, "text_summary": "Only some fields"}
        filepath = self.policy_store._get_policy_filepath("malformed_policy", 1)
        with open(filepath, 'w') as f:
            json.dump(malformed_data, f)

        loaded = self.policy_store.load_policy("malformed_policy", 1)
        # PrivacyPolicy.from_dict should raise error or return None if it handles it;
        # current from_dict might raise KeyError. The load_policy should catch this.
        self.assertIsNone(loaded)


if __name__ == '__main__':
    unittest.main()
