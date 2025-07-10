# src/privacy_framework/policy_store.py
"""
Manages persistence for PrivacyPolicy objects using JSON file storage.
"""
import os
import json
import glob
import re
from typing import Optional, List

try:
    from .policy import PrivacyPolicy
except ImportError:
    # Fallback for direct execution or different project structures
    from privacy_framework.policy import PrivacyPolicy

class PolicyStore:
    """
    Manages the storage and retrieval of PrivacyPolicy objects
    using a JSON file-based persistence mechanism.
    """

    def __init__(self, storage_path: str = "_app_data/policies/"):
        """
        Initializes the PolicyStore.

        Args:
            storage_path (str): The directory path to store policy JSON files.
        """
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            try:
                os.makedirs(self.storage_path)
            except OSError as e:
                print(f"Error creating storage directory {self.storage_path}: {e}")
                raise # Re-raise the exception if directory creation fails

        # TODO: In the future, this store could be backed by a database or
        # a decentralized storage layer (DSL) like DigiSocialBlock's DDS.

    def _get_policy_filepath(self, policy_id: str, version: int) -> str:
        """Constructs the filepath for a given policy ID and version."""
        return os.path.join(self.storage_path, f"{policy_id}_v{version}.json")

    def save_policy(self, policy: PrivacyPolicy) -> bool:
        """
        Saves a PrivacyPolicy object to a JSON file.
        Policies are considered immutable; saving a policy with an existing
        ID and version will overwrite it, but typically new versions are saved.

        Args:
            policy (PrivacyPolicy): The policy object to save.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        filepath = self._get_policy_filepath(policy.policy_id, policy.version)
        try:
            with open(filepath, 'w') as f:
                json.dump(policy.to_dict(), f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving policy {policy.policy_id} v{policy.version} to {filepath}: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred while saving policy: {e}")
            return False

    def _get_versions_for_policy(self, policy_id: str) -> List[int]:
        """Retrieves all available version numbers for a given policy_id, sorted."""
        versions = []
        pattern = os.path.join(self.storage_path, f"{policy_id}_v*.json")
        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath)
            match = re.match(rf"{policy_id}_v(\d+)\.json", filename)
            if match:
                versions.append(int(match.group(1)))
        versions.sort()
        return versions

    def _get_latest_version(self, policy_id: str) -> Optional[int]:
        """
        Finds the latest version number for a given policy ID.

        Args:
            policy_id (str): The ID of the policy.

        Returns:
            Optional[int]: The latest version number, or None if no versions found.
        """
        versions = self._get_versions_for_policy(policy_id)
        return versions[-1] if versions else None

    def load_policy(self, policy_id: str, version: Optional[int] = None) -> Optional[PrivacyPolicy]:
        """
        Loads a specific version of a policy, or the latest version if version is None.

        Args:
            policy_id (str): The ID of the policy to load.
            version (Optional[int]): The specific version to load. If None, loads the latest.

        Returns:
            Optional[PrivacyPolicy]: The loaded policy object, or None if not found or error.
        """
        if version is None:
            version = self._get_latest_version(policy_id)
            if version is None:
                # print(f"No versions found for policy_id: {policy_id}")
                return None

        filepath = self._get_policy_filepath(policy_id, version)
        if not os.path.exists(filepath):
            # print(f"Policy file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return PrivacyPolicy.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError, ValueError) as e: # Catch potential errors
            print(f"Error loading or parsing policy {policy_id} v{version} from {filepath}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while loading policy: {e}")
            return None


    def get_all_policies(self) -> List[PrivacyPolicy]:
        """
        Loads the latest version of all unique policy IDs found in the storage.

        Returns:
            List[PrivacyPolicy]: A list of PrivacyPolicy objects.
        """
        all_policy_objects = []
        policy_ids = set()

        # Find all policy files and extract policy_ids
        pattern = os.path.join(self.storage_path, "*_v*.json")
        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath)
            match = re.match(r"(.+)_v\d+\.json", filename)
            if match:
                policy_ids.add(match.group(1))

        # For each unique policy_id, load its latest version
        for policy_id in policy_ids:
            latest_policy = self.load_policy(policy_id) # This loads the latest by default
            if latest_policy:
                all_policy_objects.append(latest_policy)

        return all_policy_objects


if __name__ == '__main__':
    # Example Usage
    # Ensure this script can find the PrivacyPolicy class, e.g., by setting PYTHONPATH
    # or running from a context where 'privacy_framework' is discoverable.

    # Create a temporary storage path for the demo
    demo_storage_path = "_app_data_demo/policies_store_test/"
    if not os.path.exists(demo_storage_path):
        os.makedirs(demo_storage_path)

    policy_store = PolicyStore(storage_path=demo_storage_path)

    # Create some sample policies
    policy1_v1_data = {
        "policy_id": "test_policy_001", "version": 1,
        "data_categories": ["PERSONAL_INFO"], "purposes": ["SERVICE_DELIVERY"],
        "retention_period": "1 year", "third_parties_shared_with": [],
        "legal_basis": "CONSENT", "text_summary": "Policy 1, Version 1"
    }
    policy1_v1 = PrivacyPolicy.from_dict(policy1_v1_data)

    policy1_v2_data = {
        "policy_id": "test_policy_001", "version": 2,
        "data_categories": ["PERSONAL_INFO", "USAGE_DATA"], "purposes": ["SERVICE_DELIVERY", "ANALYTICS"],
        "retention_period": "2 years", "third_parties_shared_with": ["analytics.com"],
        "legal_basis": "CONSENT", "text_summary": "Policy 1, Version 2 (updated)"
    }
    policy1_v2 = PrivacyPolicy.from_dict(policy1_v2_data)

    policy2_v1_data = {
        "policy_id": "test_policy_002", "version": 1,
        "data_categories": ["DEVICE_INFO"], "purposes": ["SECURITY"],
        "retention_period": "90 days", "third_parties_shared_with": [],
        "legal_basis": "LEGITIMATE_INTERESTS", "text_summary": "Policy 2, Version 1"
    }
    policy2_v1 = PrivacyPolicy.from_dict(policy2_v1_data)

    print("--- Saving Policies ---")
    print(f"Saving policy1_v1: {policy_store.save_policy(policy1_v1)}")
    print(f"Saving policy1_v2: {policy_store.save_policy(policy1_v2)}")
    print(f"Saving policy2_v1: {policy_store.save_policy(policy2_v1)}")

    print("\n--- Loading Policies ---")
    loaded_p1v1 = policy_store.load_policy("test_policy_001", version=1)
    if loaded_p1v1:
        print(f"Loaded P1V1: ID={loaded_p1v1.policy_id}, Ver={loaded_p1v1.version}, Summary='{loaded_p1v1.text_summary}'")
    else:
        print("Failed to load P1V1")

    latest_p1 = policy_store.load_policy("test_policy_001") # Load latest
    if latest_p1:
        print(f"Loaded Latest P1: ID={latest_p1.policy_id}, Ver={latest_p1.version}, Summary='{latest_p1.text_summary}' (Expected V2)")
        assert latest_p1.version == 2
    else:
        print("Failed to load latest P1")

    loaded_p2 = policy_store.load_policy("test_policy_002")
    if loaded_p2:
        print(f"Loaded Latest P2: ID={loaded_p2.policy_id}, Ver={loaded_p2.version}, Summary='{loaded_p2.text_summary}'")
    else:
        print("Failed to load P2")

    non_existent = policy_store.load_policy("non_existent_policy")
    print(f"Loading non_existent_policy: {non_existent}")
    assert non_existent is None

    print("\n--- Getting All Policies (Latest Versions) ---")
    all_policies = policy_store.get_all_policies()
    print(f"Found {len(all_policies)} unique policies:")
    for p in all_policies:
        print(f"  ID={p.policy_id}, LatestVer={p.version}, Summary='{p.text_summary}'")
    assert len(all_policies) == 2 # test_policy_001 and test_policy_002

    # Clean up demo storage
    import shutil
    try:
        shutil.rmtree("_app_data_demo") # Remove the top-level demo data directory
        print("\nCleaned up demo storage directory: _app_data_demo")
    except OSError as e:
        print(f"Error removing demo storage directory: {e}")
