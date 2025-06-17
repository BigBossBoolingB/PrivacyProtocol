import unittest
import json
import os
import sys
import shutil # For cleaning up user_data directory

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.user_preferences import (
    load_user_preferences,
    save_user_preferences,
    get_default_preferences,
    DEFAULT_PREFERENCES_PATH,
    CURRENT_PREFERENCES_PATH,
    USER_DATA_DIR,
    PREFERENCE_KEYS
)

class TestUserPreferences(unittest.TestCase):
    def setUp(self):
        # Ensure a clean state for USER_DATA_DIR before each test
        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)
        os.makedirs(USER_DATA_DIR)
        # Create default preferences file for tests if it's not auto-created by get_default_preferences's fallback
        # For robustness, let's ensure it exists for tests that might only call get_default_preferences
        self.default_data = {
            "data_selling_allowed": False,
            "data_sharing_for_ads_allowed": False,
            "data_sharing_for_analytics_allowed": True,
            "cookies_for_tracking_allowed": True,
            "policy_changes_notification_required": True,
            "childrens_privacy_strict": True
        }
        with open(DEFAULT_PREFERENCES_PATH, 'w') as f:
            json.dump(self.default_data, f)

    def tearDown(self):
        # Clean up USER_DATA_DIR after each test
        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)

    def test_get_default_preferences(self):
        defaults = get_default_preferences()
        self.assertEqual(defaults, self.default_data)

    def test_load_user_preferences_no_current_file(self):
        # CURRENT_PREFERENCES_PATH should not exist initially
        self.assertFalse(os.path.exists(CURRENT_PREFERENCES_PATH))
        loaded_prefs = load_user_preferences()
        self.assertEqual(loaded_prefs, self.default_data) # Should load defaults
        self.assertTrue(os.path.exists(CURRENT_PREFERENCES_PATH)) # And create current from default
        with open(CURRENT_PREFERENCES_PATH, 'r') as f:
            current_file_data = json.load(f)
        self.assertEqual(current_file_data, self.default_data)

    def test_save_and_load_user_preferences(self):
        test_prefs = {
            "data_selling_allowed": True,
            "data_sharing_for_ads_allowed": True,
            "data_sharing_for_analytics_allowed": False,
            "cookies_for_tracking_allowed": False,
            "policy_changes_notification_required": False,
            "childrens_privacy_strict": False
        }
        self.assertTrue(save_user_preferences(test_prefs))
        loaded_prefs = load_user_preferences()
        self.assertEqual(loaded_prefs, test_prefs)

    def test_load_user_preferences_corrupted_file(self):
        with open(CURRENT_PREFERENCES_PATH, 'w') as f:
            f.write("this is not json")
        loaded_prefs = load_user_preferences()
        # Should fall back to defaults and overwrite the corrupted file
        self.assertEqual(loaded_prefs, self.default_data)
        self.assertTrue(os.path.exists(CURRENT_PREFERENCES_PATH))
        with open(CURRENT_PREFERENCES_PATH, 'r') as f:
            current_file_data = json.load(f)
        self.assertEqual(current_file_data, self.default_data)

    def test_load_user_preferences_missing_key(self):
        # Create a current preferences file with a missing key
        partial_prefs = self.default_data.copy()
        del partial_prefs["data_selling_allowed"] # Remove one key

        with open(CURRENT_PREFERENCES_PATH, 'w') as f:
            json.dump(partial_prefs, f)

        loaded_prefs = load_user_preferences()
        # Check that the missing key was added back from defaults
        self.assertIn("data_selling_allowed", loaded_prefs)
        self.assertEqual(loaded_prefs["data_selling_allowed"], self.default_data["data_selling_allowed"])
        # Ensure other keys are still there
        self.assertEqual(loaded_prefs["cookies_for_tracking_allowed"], self.default_data["cookies_for_tracking_allowed"])
        # Ensure the file was updated
        with open(CURRENT_PREFERENCES_PATH, 'r') as f:
             saved_prefs = json.load(f)
        self.assertEqual(saved_prefs, loaded_prefs) # Should now match the completed prefs
        self.assertEqual(len(saved_prefs.keys()), len(PREFERENCE_KEYS.keys()))

    def test_user_data_dir_creation(self):
        # TearDown will remove it, setUp will create it.
        # Test that load_user_preferences creates it if it's missing during the call.
        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)
        self.assertFalse(os.path.exists(USER_DATA_DIR))
        load_user_preferences() # Should create USER_DATA_DIR and current_user_preferences.json
        self.assertTrue(os.path.exists(USER_DATA_DIR))
        self.assertTrue(os.path.exists(CURRENT_PREFERENCES_PATH))

if __name__ == '__main__':
    unittest.main()
