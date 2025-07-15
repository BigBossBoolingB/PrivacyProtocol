import json
import os
from typing import List, Optional

from .privacy_policy import PrivacyPolicy

class PolicyStore:
    def __init__(self, storage_path: str = "_data/policies/"):
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def save_policy(self, policy: PrivacyPolicy) -> bool:
        """Saves a policy to a file."""
        try:
            filepath = os.path.join(self.storage_path, f"{policy.policy_id}_v{policy.version}.json")
            with open(filepath, "w") as f:
                json.dump(policy.__dict__, f, indent=4)
            return True
        except IOError:
            return False

    def load_policy(self, policy_id: str, version: Optional[int] = None) -> Optional[PrivacyPolicy]:
        """Loads a specific version of a policy, or the latest version if version is None."""
        if version is not None:
            filepath = os.path.join(self.storage_path, f"{policy_id}_v{version}.json")
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    data = json.load(f)
                    return PrivacyPolicy(**data)
            return None
        else:
            versions = []
            for filename in os.listdir(self.storage_path):
                if filename.startswith(f"{policy_id}_v") and filename.endswith(".json"):
                    try:
                        ver = int(filename.split("_v")[1].split(".json")[0])
                        versions.append(ver)
                    except (ValueError, IndexError):
                        continue
            if not versions:
                return None
            latest_version = max(versions)
            return self.load_policy(policy_id, latest_version)

    def get_all_policies(self) -> List[PrivacyPolicy]:
        """Lists all available policies."""
        policies = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_path, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)
                    policies.append(PrivacyPolicy(**data))
        return policies
