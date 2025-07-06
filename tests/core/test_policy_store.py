import unittest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime

from privacy_protocol_core.policy_store import PolicyStore
from privacy_protocol_core.policy import PrivacyPolicy # Assuming PrivacyPolicy is importable

class TestPolicyStore(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for the test PolicyStore
        self.test_dir = tempfile.mkdtemp()
        self.store = PolicyStore(base_path=self.test_dir)

        self.policy_A_v1_data = {"policy_id": "PolicyA", "version": "1.0", "text_summary": "A v1"}
        self.policy_A_v2_data = {"policy_id": "PolicyA", "version": "2.0", "text_summary": "A v2", "last_updated": datetime.now().isoformat()}
        self.policy_B_v1_data = {"policy_id": "PolicyB", "version": "1.0", "text_summary": "B v1"}
        self.policy_C_spec_chars_data = {"policy_id": "Policy:C/Special!", "version": "1.0", "text_summary": "C special"}


        self.policy_A_v1 = PrivacyPolicy.from_dict(self.policy_A_v1_data)
        self.policy_A_v2 = PrivacyPolicy.from_dict(self.policy_A_v2_data)
        self.policy_B_v1 = PrivacyPolicy.from_dict(self.policy_B_v1_data)
        self.policy_C_spec_chars = PrivacyPolicy.from_dict(self.policy_C_spec_chars_data)


    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_ensure_dir_exists(self):
        new_dir = Path(self.test_dir) / "subdir_test"
        self.assertFalse(new_dir.exists())
        self.store._ensure_dir_exists(new_dir)
        self.assertTrue(new_dir.exists())
        self.assertTrue(new_dir.is_dir())

    def test_save_policy(self):
        self.assertTrue(self.store.save_policy(self.policy_A_v1))
        expected_path = self.store._get_policy_filepath(self.policy_A_v1.policy_id, self.policy_A_v1.version)
        self.assertTrue(expected_path.exists())
        with open(expected_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data["text_summary"], self.policy_A_v1.text_summary)

    def test_save_policy_with_special_chars_in_id_and_version(self):
        policy_spec = PrivacyPolicy(policy_id="Policy/D:Special!", version="1.0-beta+build", text_summary="D special version")
        self.assertTrue(self.store.save_policy(policy_spec))
        expected_path = self.store._get_policy_filepath(policy_spec.policy_id, policy_spec.version)
        self.assertTrue(expected_path.exists(), f"File should exist at {expected_path}")
        # Ensure filename is sanitized:
        self.assertNotIn(":", expected_path.name)
        self.assertNotIn("/", expected_path.name)
        self.assertNotIn("+", expected_path.name)

        loaded = self.store.load_policy(policy_spec.policy_id, policy_spec.version)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.text_summary, "D special version")


    def test_load_specific_policy_version(self):
        self.store.save_policy(self.policy_A_v1)
        self.store.save_policy(self.policy_A_v2)

        loaded_v1 = self.store.load_policy("PolicyA", "1.0")
        self.assertIsNotNone(loaded_v1)
        self.assertEqual(loaded_v1.version, "1.0")
        self.assertEqual(loaded_v1.text_summary, "A v1")

        loaded_v2 = self.store.load_policy("PolicyA", "2.0")
        self.assertIsNotNone(loaded_v2)
        self.assertEqual(loaded_v2.version, "2.0")
        self.assertEqual(loaded_v2.text_summary, "A v2")

    def test_get_policy_versions(self):
        self.store.save_policy(self.policy_A_v1)
        self.store.save_policy(self.policy_A_v2)
        # Add another version for robust sorting test
        policy_A_v0_9 = PrivacyPolicy(policy_id="PolicyA", version="0.9", text_summary="A v0.9")
        self.store.save_policy(policy_A_v0_9)

        versions = self.store.get_policy_versions("PolicyA")
        # Expect newest first based on current sort (simple string reverse)
        # For more complex versions like '1.0.0-beta', a proper semver sort would be needed.
        # Current simple sort: '2.0', '1.0', '0.9' (if lexicographical on string versions)
        self.assertEqual(versions, ["2.0", "1.0", "0.9"])

    def test_load_latest_policy_version(self):
        self.store.save_policy(self.policy_A_v1) # Older
        self.store.save_policy(self.policy_A_v2) # Newer

        latest = self.store.load_policy("PolicyA") # Version=None means latest
        self.assertIsNotNone(latest)
        self.assertEqual(latest.version, "2.0", "Should load version 2.0 as latest")
        self.assertEqual(latest.text_summary, "A v2")

    def test_load_non_existent_policy(self):
        loaded = self.store.load_policy("NonExistentID")
        self.assertIsNone(loaded)
        loaded_version = self.store.load_policy("PolicyA", "3.0") # Assuming PolicyA only has v1,v2
        self.assertIsNone(loaded_version)

    def test_get_all_policy_ids(self):
        self.store.save_policy(self.policy_A_v1)
        self.store.save_policy(self.policy_B_v1)
        self.store.save_policy(self.policy_C_spec_chars) # ID: "Policy:C/Special!"

        ids = self.store.get_all_policy_ids()
        self.assertIn("PolicyA", ids)
        self.assertIn("PolicyB", ids)
        self.assertIn("Policy:C/Special!", ids) # Check if original ID is retrieved
        self.assertEqual(len(ids), 3)

    def test_filename_parsing(self):
        # Test _parse_version_from_filename directly
        # File "PolicyA_v1.0.json", policy_id "PolicyA" -> "1.0"
        self.assertEqual(self.store._parse_version_from_filename("PolicyA_v1.0.json", "PolicyA"), "1.0")
        # File "PolicyA_v2.0-beta.json", policy_id "PolicyA" -> "2.0-beta"
        self.assertEqual(self.store._parse_version_from_filename("PolicyA_v2.0-beta.json", "PolicyA"), "2.0-beta")
        # File "Policy_A_Internal_v1.json", policy_id "Policy_A_Internal" -> "1"
        self.assertEqual(self.store._parse_version_from_filename("Policy_A_Internal_v1.json", "Policy_A_Internal"), "1")
        # File "WrongPolicy_v1.0.json", policy_id "PolicyA" -> None
        self.assertIsNone(self.store._parse_version_from_filename("WrongPolicy_v1.0.json", "PolicyA"))
        # File "PolicyA_v1.0.json.bak", policy_id "PolicyA" -> None
        self.assertIsNone(self.store._parse_version_from_filename("PolicyA_v1.0.json.bak", "PolicyA"))
        # File "Policy_C_Special__v1.0.json" (sanitized from "Policy:C/Special!"), policy_id "Policy:C/Special!" -> "1.0"
        self.assertEqual(self.store._parse_version_from_filename("Policy_C_Special__v1.0.json", "Policy:C/Special!"), "1.0")


if __name__ == '__main__':
    unittest.main()
