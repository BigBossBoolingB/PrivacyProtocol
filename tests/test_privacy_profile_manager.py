# tests/test_privacy_profile_manager.py
import unittest
import os
import json
import shutil
import time

# Adjust import path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_profile_manager import PrivacyProfileManager, PrivacyProfile
from src.privacy_framework.policy import DataCategory, Purpose

class TestPrivacyProfileManager(unittest.TestCase):
    TEST_STORAGE_PATH = "test_user_profiles/"
    USER_ID_1 = "user_test_123"
    PROFILE_ID_1 = "profile_strict"
    PROFILE_NAME_1 = "My Strict Profile"

    def setUp(self):
        """Set up a clean storage directory for each test."""
        if os.path.exists(self.TEST_STORAGE_PATH):
            shutil.rmtree(self.TEST_STORAGE_PATH) # Remove directory and all its contents
        os.makedirs(self.TEST_STORAGE_PATH) # Recreate it empty
        self.manager = PrivacyProfileManager(storage_path=self.TEST_STORAGE_PATH)

    def tearDown(self):
        """Clean up the storage directory after each test."""
        if os.path.exists(self.TEST_STORAGE_PATH):
            shutil.rmtree(self.TEST_STORAGE_PATH)

    def test_create_profile(self):
        profile = self.manager.create_profile(
            user_id=self.USER_ID_1,
            profile_id=self.PROFILE_ID_1,
            profile_name=self.PROFILE_NAME_1,
            permitted_categories=[DataCategory.PERSONAL_INFO],
            permitted_purposes=[Purpose.SERVICE_DELIVERY],
            strictness=8
        )
        self.assertIsNotNone(profile)
        self.assertEqual(profile.profile_id, self.PROFILE_ID_1)
        self.assertEqual(profile.user_id, self.USER_ID_1)
        self.assertIn(DataCategory.PERSONAL_INFO, profile.permitted_data_categories)
        self.assertEqual(profile.strictness_level, 8)

        # Check if it's in the manager's cache
        self.assertIn(self.PROFILE_ID_1, self.manager.profiles)
        # Check if file was created
        expected_filepath = os.path.join(self.TEST_STORAGE_PATH, f"{self.PROFILE_ID_1}.json")
        self.assertTrue(os.path.exists(expected_filepath))

    def test_create_profile_duplicate_id(self):
        self.manager.create_profile(
            user_id=self.USER_ID_1,
            profile_id=self.PROFILE_ID_1,
            profile_name=self.PROFILE_NAME_1
        )
        with self.assertRaises(ValueError):
            self.manager.create_profile(
                user_id=self.USER_ID_1,
                profile_id=self.PROFILE_ID_1, # Same ID
                profile_name="Another Profile"
            )

    def test_save_and_load_profile(self):
        created_profile = self.manager.create_profile(
            user_id=self.USER_ID_1,
            profile_id="profile_to_load",
            profile_name="Test Load Profile",
            permitted_categories=[DataCategory.LOCATION_DATA],
            permitted_purposes=[Purpose.ANALYTICS]
        )

        # Clear manager's cache to force loading from disk
        self.manager.profiles = {}

        loaded_profile = self.manager.load_profile("profile_to_load")
        self.assertIsNotNone(loaded_profile)
        self.assertEqual(loaded_profile.profile_id, created_profile.profile_id)
        self.assertEqual(loaded_profile.profile_name, created_profile.profile_name)
        self.assertEqual(loaded_profile.user_id, created_profile.user_id)
        self.assertEqual(loaded_profile.permitted_data_categories, [DataCategory.LOCATION_DATA])
        self.assertEqual(loaded_profile.permitted_purposes, [Purpose.ANALYTICS])
        self.assertGreaterEqual(loaded_profile.updated_at, created_profile.created_at)

    def test_load_non_existent_profile(self):
        loaded_profile = self.manager.load_profile("non_existent_profile")
        self.assertIsNone(loaded_profile)

    def test_set_and_get_active_profile(self):
        self.manager.create_profile(
            user_id=self.USER_ID_1,
            profile_id=self.PROFILE_ID_1,
            profile_name=self.PROFILE_NAME_1
        )

        self.assertTrue(self.manager.set_active_profile(self.PROFILE_ID_1))
        active_profile = self.manager.get_active_profile()
        self.assertIsNotNone(active_profile)
        self.assertEqual(active_profile.profile_id, self.PROFILE_ID_1)

    def test_set_active_non_existent_profile(self):
        self.assertFalse(self.manager.set_active_profile("non_existent_active"))
        self.assertIsNone(self.manager.get_active_profile())

    def test_list_profiles(self):
        self.manager.create_profile(self.USER_ID_1, "prof1", "Profile 1")
        self.manager.create_profile(self.USER_ID_1, "prof2", "Profile 2")
        self.manager.create_profile("user_other_456", "prof3", "Profile 3 Other User")

        all_profiles = self.manager.list_profiles()
        self.assertEqual(len(all_profiles), 3)

        user1_profiles = self.manager.list_profiles(user_id=self.USER_ID_1)
        self.assertEqual(len(user1_profiles), 2)
        self.assertTrue(any(p.profile_id == "prof1" for p in user1_profiles))
        self.assertTrue(any(p.profile_id == "prof2" for p in user1_profiles))

    def test_load_all_profiles_from_storage_on_init(self):
        # Create some profile files manually (as if from a previous session)
        profile_data_1 = {
            "profile_id": "disk_prof_1", "profile_name": "Disk Profile 1", "user_id": "disk_user",
            "permitted_data_categories": [DataCategory.USAGE_DATA.value],
            "permitted_purposes": [Purpose.IMPROVEMENT.value],
            "created_at": int(time.time()), "updated_at": int(time.time())
        }
        with open(os.path.join(self.TEST_STORAGE_PATH, "disk_prof_1.json"), 'w') as f:
            json.dump(profile_data_1, f)

        profile_data_2 = {
            "profile_id": "disk_prof_2", "profile_name": "Disk Profile 2", "user_id": "disk_user",
            "permitted_data_categories": [], "permitted_purposes": [],
             "created_at": int(time.time()), "updated_at": int(time.time())
        }
        with open(os.path.join(self.TEST_STORAGE_PATH, "disk_prof_2.json"), 'w') as f:
            json.dump(profile_data_2, f)

        # Create a new manager instance, it should load these profiles
        new_manager = PrivacyProfileManager(storage_path=self.TEST_STORAGE_PATH)
        loaded_profiles = new_manager.list_profiles()

        self.assertEqual(len(loaded_profiles), 2)
        self.assertTrue(any(p.profile_id == "disk_prof_1" for p in loaded_profiles))
        self.assertTrue(any(p.profile_id == "disk_prof_2" for p in loaded_profiles))

        prof1_loaded = new_manager.get_profile("disk_prof_1")
        self.assertIsNotNone(prof1_loaded)
        self.assertEqual(prof1_loaded.permitted_data_categories, [DataCategory.USAGE_DATA])


    def test_profile_serialization_deserialization_edge_cases(self):
        # Test with empty lists for categories/purposes
        profile = PrivacyProfile(
            profile_id="edge_case_profile",
            profile_name="Edge Case",
            user_id="user_edge",
            permitted_data_categories=[],
            permitted_purposes=[],
            trusted_third_parties=[],
            blocked_third_parties=[]
        )
        profile_json = profile.to_json()
        loaded_profile = PrivacyProfile.from_json(profile_json)

        self.assertEqual(loaded_profile.permitted_data_categories, [])
        self.assertEqual(loaded_profile.permitted_purposes, [])
        self.assertEqual(loaded_profile.trusted_third_parties, [])


if __name__ == '__main__':
    unittest.main()
