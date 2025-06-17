import json
import os

# Define paths relative to this file's location (privacy_protocol/privacy_protocol/)
USER_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'user_data')
DEFAULT_PREFERENCES_PATH = os.path.join(USER_DATA_DIR, 'default_preferences.json')
CURRENT_PREFERENCES_PATH = os.path.join(USER_DATA_DIR, 'current_user_preferences.json')

# Define the expected preference keys and their default types for validation (optional but good)
PREFERENCE_KEYS = {
    "data_selling_allowed": bool,
    "data_sharing_for_ads_allowed": bool,
    "data_sharing_for_analytics_allowed": bool,
    "cookies_for_tracking_allowed": bool,
    "policy_changes_notification_required": bool,
    "childrens_privacy_strict": bool
}

def get_default_preferences():
    """Loads the default preferences."""
    try:
        with open(DEFAULT_PREFERENCES_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to hardcoded defaults if file is missing/corrupt, though it should exist
        return {
            "data_selling_allowed": False,
            "data_sharing_for_ads_allowed": False,
            "data_sharing_for_analytics_allowed": True,
            "cookies_for_tracking_allowed": True,
            "policy_changes_notification_required": True,
            "childrens_privacy_strict": True
        }

def load_user_preferences():
    """Loads current user preferences, falling back to defaults if not found or invalid."""
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)
        print(f"Created directory: {USER_DATA_DIR}")

    try:
        if not os.path.exists(CURRENT_PREFERENCES_PATH):
            # If current preferences don't exist, copy from default
            prefs = get_default_preferences()
            save_user_preferences(prefs)
            return prefs
        else:
            with open(CURRENT_PREFERENCES_PATH, 'r') as f:
                prefs = json.load(f)
                # Basic validation: ensure all keys are present and have correct types (optional)
                valid = True
                default_prefs_for_keys = get_default_preferences() # To get all keys
                for key in default_prefs_for_keys.keys():
                    if key not in prefs: # or not isinstance(prefs[key], PREFERENCE_KEYS[key]):
                        # If a key is missing, copy it from default and mark for re-saving
                        prefs[key] = default_prefs_for_keys[key]
                        valid = False # Mark as 'invalid' to trigger a re-save with the new key
                if not valid:
                    save_user_preferences(prefs) # Save back to ensure new keys are persisted
                return prefs
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to default if current is corrupt or becomes unreadable
        prefs = get_default_preferences()
        save_user_preferences(prefs) # Attempt to save defaults back
        return prefs

def save_user_preferences(preferences_data):
    """Saves the given preferences data to the current user preferences file."""
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)
        print(f"Created directory: {USER_DATA_DIR}")
    try:
        with open(CURRENT_PREFERENCES_PATH, 'w') as f:
            json.dump(preferences_data, f, indent=4)
        return True
    except IOError:
        return False # Failed to save

if __name__ == '__main__':
    print("User Preferences Management Script")
    print(f"Default preferences path: {DEFAULT_PREFERENCES_PATH}")
    print(f"Current preferences path: {CURRENT_PREFERENCES_PATH}")

    # Ensure user_data directory exists
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)
        print(f"Created user_data directory at: {USER_DATA_DIR}")

    # Test loading (and creating if not exist)
    current_prefs = load_user_preferences()
    print("\nLoaded current preferences:")
    for key, value in current_prefs.items():
        print(f"  {key}: {value}")

    # Test saving (example modification)
    # current_prefs['data_selling_allowed'] = True
    # if save_user_preferences(current_prefs):
    #     print("\nSuccessfully saved modified preferences.")
    # else:
    #     print("\nFailed to save preferences.")

    # print("\nReloaded preferences after potential save:")
    # current_prefs = load_user_preferences()
    # for key, value in current_prefs.items():
    #     print(f"  {key}: {value}")

    print("\nDefault preferences:")
    default_prefs = get_default_preferences()
    for key, value in default_prefs.items():
        print(f"  {key}: {value}")
