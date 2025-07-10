# src/privacy_framework/consent_store.py
"""
Manages persistence for UserConsent objects using JSON file storage.
"""
import os
import json
import glob
from typing import Optional, List

try:
    from .consent import UserConsent
except ImportError:
    # Fallback for direct execution or different project structures
    from privacy_framework.consent import UserConsent

class ConsentStore:
    """
    Manages the storage and retrieval of UserConsent objects
    using a JSON file-based persistence mechanism.
    """

    def __init__(self, storage_path: str = "_app_data/consents/"):
        """
        Initializes the ConsentStore.

        Args:
            storage_path (str): The base directory path to store consent JSON files.
                                User-specific subdirectories will be created under this path.
        """
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            try:
                os.makedirs(self.storage_path)
            except OSError as e:
                print(f"Error creating base consent storage directory {self.storage_path}: {e}")
                raise

        # TODO: Future - Consider integration with EmPower1 Blockchain for verifiable consent records.

    def _get_user_consent_dir(self, user_id: str) -> str:
        """Constructs the directory path for a given user's consents."""
        return os.path.join(self.storage_path, user_id)

    def _get_consent_filepath(self, user_id: str, consent_id: str) -> str:
        """Constructs the filepath for a given consent_id within a user's directory."""
        user_dir = self._get_user_consent_dir(user_id)
        return os.path.join(user_dir, f"{consent_id}.json")

    def save_consent(self, consent: UserConsent) -> bool:
        """
        Saves a UserConsent object to a JSON file in a user-specific directory.
        The filename will be <consent_id>.json.

        Args:
            consent (UserConsent): The consent object to save.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        user_dir = self._get_user_consent_dir(consent.user_id)
        if not os.path.exists(user_dir):
            try:
                os.makedirs(user_dir)
            except OSError as e:
                print(f"Error creating user consent directory {user_dir}: {e}")
                return False

        filepath = self._get_consent_filepath(consent.user_id, consent.consent_id)
        try:
            with open(filepath, 'w') as f:
                json.dump(consent.to_dict(), f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving consent {consent.consent_id} to {filepath}: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred while saving consent: {e}")
            return False

    def load_consent(self, user_id: str, consent_id: str) -> Optional[UserConsent]:
        """
        Loads a specific consent record by its ID for a given user.

        Args:
            user_id (str): The ID of the user whose consent is being loaded.
            consent_id (str): The ID of the consent record.

        Returns:
            Optional[UserConsent]: The loaded UserConsent object, or None if not found or error.
        """
        filepath = self._get_consent_filepath(user_id, consent_id)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                # TODO: Future - Verify cryptographic signature here if present (data.get("signature"))
                #       using DigiSocialBlock's identity system / user's public key.
                return UserConsent.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading or parsing consent {consent_id} from {filepath}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while loading consent: {e}")
            return None

    def load_all_consents_for_user(self, user_id: str) -> List[UserConsent]:
        """
        Loads all consent records for a specific user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            List[UserConsent]: A list of UserConsent objects, sorted by timestamp descending.
        """
        user_dir = self._get_user_consent_dir(user_id)
        if not os.path.exists(user_dir):
            return []

        consents: List[UserConsent] = []
        pattern = os.path.join(user_dir, "*.json")
        for filepath in glob.glob(pattern):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    # TODO: Future - Verify cryptographic signature here.
                    consent_obj = UserConsent.from_dict(data)
                    consents.append(consent_obj)
            except (IOError, json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Skipping file {filepath} due to load/parse error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while loading a consent file {filepath}: {e}")

        # Sort by timestamp, most recent first
        consents.sort(key=lambda c: c.timestamp, reverse=True)
        return consents

    def load_latest_active_consent(self, user_id: str, policy_id: str) -> Optional[UserConsent]:
        """
        Loads the most recent, active consent for a specific user and policy_id.

        Args:
            user_id (str): The ID of the user.
            policy_id (str): The ID of the policy.

        Returns:
            Optional[UserConsent]: The most recent active UserConsent object, or None if none found.
        """
        user_consents = self.load_all_consents_for_user(user_id)

        latest_active_consent: Optional[UserConsent] = None
        for consent in user_consents:
            if consent.policy_id == policy_id and consent.is_active:
                if latest_active_consent is None or consent.timestamp > latest_active_consent.timestamp:
                    latest_active_consent = consent

        return latest_active_consent

if __name__ == '__main__':
    # Example Usage
    demo_consent_storage_path = "_app_data_demo/consents_store_test/"
    if not os.path.exists(demo_consent_storage_path):
        os.makedirs(demo_consent_storage_path)

    consent_store = ConsentStore(storage_path=demo_consent_storage_path)

    user1 = "user_jane_doe"
    policy1 = "newsletter_policy_v1.2"
    policy2 = "app_usage_policy_v3.0"

    # Create and save some consents
    consent1_data = {
        "consent_id": "consent_jane_news_1678886400", "user_id": user1, "policy_id": policy1, "version": 1,
        "data_categories_consented": ["PERSONAL_INFO"], "purposes_consented": ["MARKETING"],
        "third_parties_consented": ["mailservice.com"], "timestamp": 1678886400, "is_active": True
    }
    consent1 = UserConsent.from_dict(consent1_data)
    print(f"Saving consent1: {consent_store.save_consent(consent1)}")

    consent2_data = {
        "consent_id": "consent_jane_news_1678887000_revoked", "user_id": user1, "policy_id": policy1, "version": 1,
        "data_categories_consented": ["PERSONAL_INFO"], "purposes_consented": [], # No purposes
        "third_parties_consented": [], "timestamp": 1678887000, "is_active": False # Revoked
    }
    consent2_revoked = UserConsent.from_dict(consent2_data)
    print(f"Saving consent2 (revoked): {consent_store.save_consent(consent2_revoked)}")

    consent3_data = {
        "consent_id": "consent_jane_app_1678887200", "user_id": user1, "policy_id": policy2, "version": 3,
        "data_categories_consented": ["USAGE_DATA", "DEVICE_INFO"], "purposes_consented": ["ANALYTICS", "IMPROVEMENT"],
        "third_parties_consented": [], "timestamp": 1678887200, "is_active": True
    }
    consent3 = UserConsent.from_dict(consent3_data)
    print(f"Saving consent3: {consent_store.save_consent(consent3)}")

    consent4_data_older_active_news = { # Older but active for newsletter policy
        "consent_id": "consent_jane_news_1678886000_older_active", "user_id": user1, "policy_id": policy1, "version": 1,
        "data_categories_consented": ["PERSONAL_INFO"], "purposes_consented": ["MARKETING"],
        "third_parties_consented": [], "timestamp": 1678886000, "is_active": True
    }
    consent4 = UserConsent.from_dict(consent4_data_older_active_news)
    print(f"Saving consent4 (older active for news): {consent_store.save_consent(consent4)}")


    print("\n--- Loading Consents ---")
    loaded_c1 = consent_store.load_consent(user1, "consent_jane_news_1678886400")
    if loaded_c1:
        print(f"Loaded C1: ID={loaded_c1.consent_id}, Active={loaded_c1.is_active}")
    else:
        print("Failed to load C1")

    print("\n--- Loading Latest Active Consents ---")
    latest_active_news = consent_store.load_latest_active_consent(user1, policy1)
    if latest_active_news:
        print(f"Latest active for '{policy1}': ID={latest_active_news.consent_id}, Timestamp={latest_active_news.timestamp} (Expected consent1 or consent4 based on timestamp)")
        # consent1 (ts=1678886400) should be later than consent4 (ts=1678886000)
        assert latest_active_news.consent_id == "consent_jane_news_1678886400"
    else:
        print(f"No active consent found for {user1}/{policy1}")

    latest_active_app = consent_store.load_latest_active_consent(user1, policy2)
    if latest_active_app:
        print(f"Latest active for '{policy2}': ID={latest_active_app.consent_id}, Timestamp={latest_active_app.timestamp}")
        assert latest_active_app.consent_id == "consent_jane_app_1678887200"
    else:
        print(f"No active consent found for {user1}/{policy2}")

    latest_active_nonexistent_policy = consent_store.load_latest_active_consent(user1, "non_existent_policy")
    print(f"Latest active for 'non_existent_policy': {latest_active_nonexistent_policy}")
    assert latest_active_nonexistent_policy is None

    print("\n--- Loading All Consents for User ---")
    all_jane_consents = consent_store.load_all_consents_for_user(user1)
    print(f"Found {len(all_jane_consents)} consents for {user1}:")
    for c in all_jane_consents:
        print(f"  ID={c.consent_id}, Policy={c.policy_id}, Active={c.is_active}, Timestamp={c.timestamp}")
    assert len(all_jane_consents) == 4
    # Check sorting (most recent first)
    assert all_jane_consents[0].timestamp >= all_jane_consents[1].timestamp

    # Clean up demo storage
    import shutil
    try:
        shutil.rmtree("_app_data_demo")
        print("\nCleaned up demo storage directory: _app_data_demo")
    except OSError as e:
        print(f"Error removing demo storage directory: {e}")
