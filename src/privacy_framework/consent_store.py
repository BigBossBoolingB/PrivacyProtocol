import json
import os
import datetime
from typing import List, Optional

from .user_consent import UserConsent

class ConsentStore:
    """
    Manages the storage and retrieval of UserConsent objects using JSON file persistence.
    """
    def __init__(self, storage_path: str = "_data/consents/"):
        """
        Initializes the ConsentStore.

        Args:
            storage_path (str): The directory where consents will be stored.
        """
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def save_consent(self, consent: UserConsent) -> bool:
        """
        Saves a consent record to a file.

        Args:
            consent (UserConsent): The consent record to save.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        try:
            user_dir = os.path.join(self.storage_path, consent.user_id)
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)

            timestamp_str = consent.timestamp.isoformat().replace(":", "-")
            filepath = os.path.join(user_dir, f"{consent.policy_id}_{consent.consent_id}_{timestamp_str}.json")

            with open(filepath, "w") as f:
                json.dump(consent.__dict__, f, default=str, indent=4)
            return True
        except IOError:
            return False

    def load_latest_consent(self, user_id: str, policy_id: str) -> Optional[UserConsent]:
        """
        Loads the most recent active consent for a user and policy.

        Args:
            user_id (str): The ID of the user.
            policy_id (str): The ID of the policy.

        Returns:
            Optional[UserConsent]: The latest active consent, or None if not found.
        """
        user_dir = os.path.join(self.storage_path, user_id)
        if not os.path.exists(user_dir):
            return None

        latest_consent = None
        latest_timestamp = None

        for filename in os.listdir(user_dir):
            if filename.startswith(f"{policy_id}_") and filename.endswith(".json"):
                filepath = os.path.join(user_dir, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)
                    # Convert timestamp string back to datetime object
                    data['timestamp'] = datetime.datetime.fromisoformat(data['timestamp'])

                    if data.get('granted'):
                        if latest_timestamp is None or data['timestamp'] > latest_timestamp:
                            latest_timestamp = data['timestamp']
                            latest_consent = UserConsent(**data)
        return latest_consent

    def load_all_consents(self, user_id: str) -> List[UserConsent]:
        """
        Loads all consent records for a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            List[UserConsent]: A list of all consent records for the user.
        """
        user_dir = os.path.join(self.storage_path, user_id)
        if not os.path.exists(user_dir):
            return []

        consents = []
        for filename in os.listdir(user_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(user_dir, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)
                    # Convert timestamp string back to datetime object
                    data['timestamp'] = datetime.datetime.fromisoformat(data['timestamp'])
                    consents.append(UserConsent(**data))
        return consents
