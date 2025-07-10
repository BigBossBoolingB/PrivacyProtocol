# tests/test_consent_store.py
import unittest
import os
import shutil
import json
import time

# Adjust import path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.consent import UserConsent
from src.privacy_framework.policy import DataCategory, Purpose # For creating UserConsent instances
from src.privacy_framework.consent_store import ConsentStore

class TestConsentStore(unittest.TestCase):
    BASE_TEST_STORAGE_PATH = "_app_data_test/test_consents/"
    USER_ID_1 = "user_consent_store_test_001"
    USER_ID_2 = "user_consent_store_test_002"
    POLICY_ID_1 = "policy_for_consent_A"
    POLICY_ID_2 = "policy_for_consent_B"

    def setUp(self):
        """Set up a clean storage directory for each test."""
        if os.path.exists(self.BASE_TEST_STORAGE_PATH):
            shutil.rmtree(self.BASE_TEST_STORAGE_PATH)
        # ConsentStore constructor will create the base path
        self.consent_store = ConsentStore(storage_path=self.BASE_TEST_STORAGE_PATH)

        # Sample Consents
        self.consent1_user1_policy1_time1 = UserConsent(
            consent_id="c1u1p1t1", user_id=self.USER_ID_1, policy_id=self.POLICY_ID_1, version=1,
            data_categories_consented=[DataCategory.PERSONAL_INFO], purposes_consented=[Purpose.SERVICE_DELIVERY],
            timestamp=int(time.time()) - 200, is_active=True
        )
        self.consent2_user1_policy1_time2 = UserConsent( # Newer for same user/policy
            consent_id="c2u1p1t2", user_id=self.USER_ID_1, policy_id=self.POLICY_ID_1, version=1,
            data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
            purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
            timestamp=int(time.time()) - 100, is_active=True
        )
        self.consent3_user1_policy1_time3_inactive = UserConsent( # Newest but inactive
            consent_id="c3u1p1t3", user_id=self.USER_ID_1, policy_id=self.POLICY_ID_1, version=1,
            data_categories_consented=[DataCategory.PERSONAL_INFO], purposes_consented=[Purpose.MARKETING],
            timestamp=int(time.time()) - 50, is_active=False
        )
        self.consent4_user1_policy2_time1 = UserConsent( # Different policy for user1
            consent_id="c4u1p2t1", user_id=self.USER_ID_1, policy_id=self.POLICY_ID_2, version=1,
            data_categories_consented=[DataCategory.DEVICE_INFO], purposes_consented=[Purpose.SECURITY],
            timestamp=int(time.time()) - 150, is_active=True
        )
        self.consent5_user2_policy1_time1 = UserConsent( # Different user
            consent_id="c5u2p1t1", user_id=self.USER_ID_2, policy_id=self.POLICY_ID_1, version=1,
            data_categories_consented=[DataCategory.LOCATION_DATA], purposes_consented=[Purpose.PERSONALIZATION],
            timestamp=int(time.time()) - 180, is_active=True
        )

    def tearDown(self):
        """Clean up the storage directory after each test."""
        if os.path.exists(self.BASE_TEST_STORAGE_PATH):
            shutil.rmtree(self.BASE_TEST_STORAGE_PATH)

    def test_user_directory_creation_on_save(self):
        user_dir = os.path.join(self.BASE_TEST_STORAGE_PATH, self.USER_ID_1)
        self.assertFalse(os.path.exists(user_dir))
        self.consent_store.save_consent(self.consent1_user1_policy1_time1)
        self.assertTrue(os.path.exists(user_dir))

    def test_save_and_load_consent(self):
        self.assertTrue(self.consent_store.save_consent(self.consent1_user1_policy1_time1))

        loaded = self.consent_store.load_consent(
            self.consent1_user1_policy1_time1.user_id,
            self.consent1_user1_policy1_time1.consent_id
        )
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.consent_id, self.consent1_user1_policy1_time1.consent_id)
        self.assertEqual(loaded.policy_id, self.consent1_user1_policy1_time1.policy_id)
        self.assertEqual(loaded.purposes_consented, self.consent1_user1_policy1_time1.purposes_consented)

    def test_load_non_existent_consent(self):
        self.assertIsNone(self.consent_store.load_consent(self.USER_ID_1, "non_existent_consent_id"))

    def test_load_consent_from_non_existent_user_dir(self):
        self.assertIsNone(self.consent_store.load_consent("non_existent_user", "any_id"))

    def test_load_all_consents_for_user(self):
        self.consent_store.save_consent(self.consent1_user1_policy1_time1)
        self.consent_store.save_consent(self.consent2_user1_policy1_time2)
        self.consent_store.save_consent(self.consent3_user1_policy1_time3_inactive)
        self.consent_store.save_consent(self.consent4_user1_policy2_time1)
        self.consent_store.save_consent(self.consent5_user2_policy1_time1) # Different user

        user1_consents = self.consent_store.load_all_consents_for_user(self.USER_ID_1)
        self.assertEqual(len(user1_consents), 4)
        # Check if sorted by timestamp descending
        self.assertEqual(user1_consents[0].consent_id, self.consent3_user1_policy1_time3_inactive.consent_id)
        self.assertEqual(user1_consents[1].consent_id, self.consent2_user1_policy1_time2.consent_id)
        self.assertEqual(user1_consents[2].consent_id, self.consent4_user1_policy2_time1.consent_id)
        self.assertEqual(user1_consents[3].consent_id, self.consent1_user1_policy1_time1.consent_id)

    def test_load_all_consents_for_non_existent_user(self):
        consents = self.consent_store.load_all_consents_for_user("ghost_user")
        self.assertEqual(len(consents), 0)

    def test_load_latest_active_consent(self):
        self.consent_store.save_consent(self.consent1_user1_policy1_time1) # active, time -200
        self.consent_store.save_consent(self.consent2_user1_policy1_time2) # active, time -100 (latest active for policy1)
        self.consent_store.save_consent(self.consent3_user1_policy1_time3_inactive) # inactive, time -50

        latest_active = self.consent_store.load_latest_active_consent(self.USER_ID_1, self.POLICY_ID_1)
        self.assertIsNotNone(latest_active)
        self.assertEqual(latest_active.consent_id, self.consent2_user1_policy1_time2.consent_id)

    def test_load_latest_active_consent_none_active(self):
        self.consent_store.save_consent(self.consent3_user1_policy1_time3_inactive) # Only one, and it's inactive
        latest_active = self.consent_store.load_latest_active_consent(self.USER_ID_1, self.POLICY_ID_1)
        self.assertIsNone(latest_active)

    def test_load_latest_active_consent_no_consents_for_policy(self):
        self.consent_store.save_consent(self.consent4_user1_policy2_time1) # Consent for POLICY_ID_2
        latest_active = self.consent_store.load_latest_active_consent(self.USER_ID_1, self.POLICY_ID_1) # Query for POLICY_ID_1
        self.assertIsNone(latest_active)

    def test_persistence_across_instances(self):
        self.consent_store.save_consent(self.consent1_user1_policy1_time1)

        new_store = ConsentStore(storage_path=self.BASE_TEST_STORAGE_PATH)
        loaded_consent = new_store.load_consent(
            self.consent1_user1_policy1_time1.user_id,
            self.consent1_user1_policy1_time1.consent_id
        )
        self.assertIsNotNone(loaded_consent)
        self.assertEqual(loaded_consent.policy_id, self.consent1_user1_policy1_time1.policy_id)

    def test_handle_invalid_json_file(self):
        user_dir = self.consent_store._get_user_consent_dir(self.USER_ID_1)
        os.makedirs(user_dir, exist_ok=True)
        filepath = os.path.join(user_dir, "corrupted_consent.json")
        with open(filepath, 'w') as f:
            f.write("{'invalid_json': True,") # Missing closing brace, single quotes

        # load_all_consents_for_user should skip this file
        consents = self.consent_store.load_all_consents_for_user(self.USER_ID_1)
        self.assertEqual(len(consents), 0)

        # load_consent should return None
        loaded = self.consent_store.load_consent(self.USER_ID_1, "corrupted_consent")
        self.assertIsNone(loaded)

    def test_handle_malformed_consent_data(self):
        malformed_data = {"consent_id": "malformed", "user_id": self.USER_ID_1, "policy_id": "p1"} # Missing fields
        filepath = self.consent_store._get_consent_filepath(self.USER_ID_1, "malformed_consent")
        user_dir = os.path.dirname(filepath)
        os.makedirs(user_dir, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(malformed_data, f)

        loaded = self.consent_store.load_consent(self.USER_ID_1, "malformed_consent")
        self.assertIsNone(loaded) # UserConsent.from_dict should fail gracefully or raise error caught by load_consent

if __name__ == '__main__':
    unittest.main()
