import json
import os
import glob
from pathlib import Path
import re
from typing import Optional, List

try:
    from .policy import PrivacyPolicy
except ImportError: # For standalone testing
    from policy import PrivacyPolicy

class PolicyStore:
    def __init__(self, base_path: str = "./_data/policies/"):
        self.base_path = Path(base_path)
        self._ensure_dir_exists(self.base_path)

    def _ensure_dir_exists(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

    def _get_policy_filepath(self, policy_id: str, version: str) -> Path:
        # Sanitize policy_id and version to be safe filenames
        safe_policy_id = re.sub(r'[^\w\-.]', '_', policy_id)
        safe_version = re.sub(r'[^\w\-.]', '_', version)
        return self.base_path / f"{safe_policy_id}_v{safe_version}.json"

    def save_policy(self, policy: PrivacyPolicy) -> bool:
        if not isinstance(policy, PrivacyPolicy):
            raise ValueError("Invalid policy object provided.")

        filepath = self._get_policy_filepath(policy.policy_id, policy.version)
        try:
            with open(filepath, 'w') as f:
                json.dump(policy.to_dict(), f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving policy {policy.policy_id} v{policy.version}: {e}")
            return False

    def _parse_version_from_filename(self, filename: str, policy_id: str) -> Optional[str]:
        # Filename format: <policy_id>_v<version>.json
        # Ensure policy_id part matches to avoid conflicts if policy_ids can be substrings of others
        safe_policy_id = re.sub(r'[^\w\-.]', '_', policy_id)
        match = re.fullmatch(rf"{re.escape(safe_policy_id)}_v([\w\-.]+)\.json", Path(filename).name)
        if match:
            return match.group(1)
        return None

    def get_policy_versions(self, policy_id: str) -> List[str]:
        versions = []
        safe_policy_id = re.sub(r'[^\w\-.]', '_', policy_id)
        pattern = self.base_path / f"{safe_policy_id}_v*.json"

        for filepath in glob.glob(str(pattern)):
            filename = Path(filepath).name
            version = self._parse_version_from_filename(filename, policy_id)
            if version:
                versions.append(version)

        # Sort versions (lexicographical sort might be okay for simple x.y.z, but proper semver sort is better)
        # For now, simple sort. Consider packaging `packaging.version` for robust sorting if needed.
        versions.sort(reverse=True) # Simplistic: newest first by string sort
        return versions

    def load_policy(self, policy_id: str, version: Optional[str] = None) -> Optional[PrivacyPolicy]:
        if version is None: # Load latest version
            available_versions = self.get_policy_versions(policy_id)
            if not available_versions:
                return None
            version = available_versions[0] # Assumes get_policy_versions sorts newest first

        filepath = self._get_policy_filepath(policy_id, version)
        if filepath.exists() and filepath.is_file():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return PrivacyPolicy.from_dict(data)
            except (IOError, json.JSONDecodeError, ValueError) as e: # Added ValueError for from_dict issues
                print(f"Error loading policy {policy_id} v{version}: {e}")
                return None
        return None

    def get_all_policy_ids(self) -> List[str]:
        policy_ids = set()
        pattern = self.base_path / "*.json" # Matches all json files
        for filepath in glob.glob(str(pattern)):
            filename = Path(filepath).name
            # Extract policy_id part: everything before the first occurrence of "_v"
            match = re.match(r"([^_]+(?:_[^_]+)*)_v[\w\-.]+\.json", filename)
            if match:
                # This regex for policy_id extraction assumes policy_id itself doesn't contain "_v"
                # A safer way might be to store original policy_ids if they could be complex
                # For now, this assumes simple policy_ids or that the extracted part is the ID
                # Re-sanitize might be needed if original IDs had chars that were replaced by '_'
                # This part is tricky without knowing the exact original policy_id format.
                # For now, let's assume the part before "_v" is usable, but this is a simplification.
                # A better way: store policies in subdirs: policies/<policy_id>/<version>.json

                # Simplification: Assume filename starts with safe_policy_id
                # This requires knowing all possible original policy_ids to test against the filename start.
                # This is hard. A directory per policy_id is much more robust.
                # For now, a rough extraction and then relying on get_policy_versions to confirm.

                # Let's refine: extract up to the LAST "_v"
                id_part_match = re.match(r"(.*)_v[\w\-.]+\.json", filename)
                if id_part_match:
                    # This extracted id_part might be the "safe" version.
                    # We need to map it back to an original ID or assume it's the ID.
                    # This is where a manifest file or dir structure would be better.
                    # For now, we'll add it and let get_policy_versions filter later.
                    policy_ids.add(id_part_match.group(1))


        # This list might contain "safe" versions of IDs. True unique ID retrieval is hard with flat structure.
        # The current implementation of get_policy_versions requires the original policy_id.
        # So, this method is more of a "get all potential base filenames"
        # A proper implementation would need a manifest or directory structure.
        # For the plan, this is a placeholder for a more robust solution.
        # Let's return unique file prefixes for now.

        # Revised approach for get_all_policy_ids:
        # Iterate through files, parse (policy_id, version) from filename. Store unique policy_ids.
        # This assumes we can reliably parse original policy_id from filename, which is hard if it was sanitized.
        # Given the _get_policy_filepath sanitizes, we can't easily reverse this to get original IDs.
        # The current plan to use this class is via specific policy_id lookups.
        # So, this method is less critical for the immediate next steps but highlights a design challenge.
        # For now, returning an empty list or raising NotImplementedError is safer than returning potentially incorrect IDs.
        # Or, we can scan and try to parse the content of each file to get the actual policy_id.

        actual_policy_ids = set()
        for filepath_str in glob.glob(str(self.base_path / "*.json")):
            filepath = Path(filepath_str)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if "policy_id" in data:
                        actual_policy_ids.add(data["policy_id"])
            except Exception: # Ignore files that can't be read or parsed
                pass
        return list(actual_policy_ids)


if __name__ == '__main__':
    # Example Usage (requires PrivacyPolicy class from policy.py)
    # Create a temporary directory for testing
    import tempfile
    import shutil
    from datetime import datetime

    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory for PolicyStore: {temp_dir}")
    store = PolicyStore(base_path=temp_dir)

    # Create sample policies
    policy_A_v1 = PrivacyPolicy(policy_id="PolicyA", version="1.0", text_summary="Policy A version 1.0")
    policy_A_v2 = PrivacyPolicy(policy_id="PolicyA", version="2.0", text_summary="Policy A version 2.0", last_updated=(datetime.now()).isoformat())
    policy_B_v1 = PrivacyPolicy(policy_id="PolicyB", version="1.0", text_summary="Policy B version 1.0")
    policy_C_id_with_chars = PrivacyPolicy(policy_id="Policy/C:Special!", version="1.0", text_summary="Policy C with special chars in ID")


    # Save policies
    print(f"Saving PolicyA v1.0: {store.save_policy(policy_A_v1)}")
    print(f"Saving PolicyA v2.0: {store.save_policy(policy_A_v2)}")
    print(f"Saving PolicyB v1.0: {store.save_policy(policy_B_v1)}")
    print(f"Saving Policy/C:Special! v1.0: {store.save_policy(policy_C_id_with_chars)}")


    # List versions for PolicyA
    versions_A = store.get_policy_versions("PolicyA")
    print(f"Versions for PolicyA: {versions_A}") # Expected: ['2.0', '1.0'] (or similar, depends on sort)
    assert "2.0" in versions_A
    assert "1.0" in versions_A

    versions_C = store.get_policy_versions("Policy/C:Special!")
    print(f"Versions for Policy/C:Special!: {versions_C}")
    assert "1.0" in versions_C


    # Load specific version
    loaded_A_v1 = store.load_policy("PolicyA", "1.0")
    if loaded_A_v1:
        print(f"Loaded PolicyA v1.0: ID={loaded_A_v1.policy_id}, Summary='{loaded_A_v1.text_summary}'")
        assert loaded_A_v1.text_summary == "Policy A version 1.0"
    else:
        print("Failed to load PolicyA v1.0")

    # Load latest version of PolicyA
    latest_A = store.load_policy("PolicyA")
    if latest_A:
        print(f"Loaded latest PolicyA: ID={latest_A.policy_id}, Version={latest_A.version}, Summary='{latest_A.text_summary}'")
        assert latest_A.version == "2.0" # Assuming simple string sort puts 2.0 before 1.0 if reverse=True
    else:
        print("Failed to load latest PolicyA")

    loaded_C = store.load_policy("Policy/C:Special!")
    if loaded_C:
        print(f"Loaded latest Policy/C:Special!: ID={loaded_C.policy_id}, Version={loaded_C.version}")
        assert loaded_C.policy_id == "Policy/C:Special!"
    else:
        print("Failed to load Policy/C:Special!")


    # List all policy IDs
    all_ids = store.get_all_policy_ids()
    print(f"All policy IDs in store: {all_ids}")
    assert "PolicyA" in all_ids
    assert "PolicyB" in all_ids
    assert "Policy/C:Special!" in all_ids


    # Test loading non-existent policy
    non_existent = store.load_policy("NonExistentPolicy")
    print(f"Loading NonExistentPolicy: {non_existent}")
    assert non_existent is None

    # Clean up temporary directory
    try:
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        print(f"Error cleaning up temp directory {temp_dir}: {e}")

    print("PolicyStore examples finished.")
