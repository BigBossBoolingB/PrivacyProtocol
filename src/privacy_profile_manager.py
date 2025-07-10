# src/privacy_profile_manager.py
"""
Defines Personalized Privacy Profiles and a manager for them.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import os
import time

# Attempting to import from sibling directory `privacy_framework`
try:
    from .privacy_framework.policy import DataCategory, Purpose
    from .privacy_framework.consent import UserConsent
except ImportError:
    # Fallback for direct execution or different project structures
    from privacy_framework.policy import DataCategory, Purpose
    from privacy_framework.consent import UserConsent


@dataclass
class PrivacyProfile:
    """
    Represents a user's personalized privacy profile with their preferences.
    """
    profile_id: str
    profile_name: str
    user_id: str  # Link to the user this profile belongs to

    # Granular preferences
    # User specifies which categories of data they are generally willing to share
    permitted_data_categories: List[DataCategory] = field(default_factory=list)
    # User specifies for which purposes they generally allow data usage
    permitted_purposes: List[Purpose] = field(default_factory=list)
    # User specifies a list of third parties they generally trust or distrust (can be more complex)
    trusted_third_parties: List[str] = field(default_factory=list)
    blocked_third_parties: List[str] = field(default_factory=list)

    # Default consent action for new policies/services (e.g., "ASK_ME", "APPLY_PROFILE_STRICT", "APPLY_PROFILE_LENIENT")
    default_action: str = "ASK_ME"

    # Simple way to define overall strictness (could be an enum or numeric)
    strictness_level: int = 5  # e.g., 1 (most lenient) to 10 (most strict)

    created_at: int = field(default_factory=lambda: int(time.time()))
    updated_at: int = field(default_factory=lambda: int(time.time()))

    def to_dict(self) -> Dict[str, Any]:
        """Converts the PrivacyProfile object to a dictionary for serialization."""
        # Use asdict for dataclasses, then handle enums
        data = asdict(self)
        data["permitted_data_categories"] = [cat.value for cat in self.permitted_data_categories]
        data["permitted_purposes"] = [purp.value for purp in self.permitted_purposes]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrivacyProfile":
        """Creates a PrivacyProfile object from a dictionary."""
        # Convert enum string values back to Enum members
        data["permitted_data_categories"] = [DataCategory(cat) for cat in data.get("permitted_data_categories", [])]
        data["permitted_purposes"] = [Purpose(purp) for purp in data.get("permitted_purposes", [])]

        # Ensure all fields expected by the dataclass are present
        # This is a simplified version; a more robust solution might involve checking all fields
        # or using a library like Pydantic for validation.

        # field_names = {f.name for f in fields(cls)}
        # filtered_data = {k: v for k, v in data.items() if k in field_names}
        # # ^ This is more robust but fields() needs to be imported from dataclasses

        return cls(
            profile_id=data["profile_id"],
            profile_name=data["profile_name"],
            user_id=data["user_id"],
            permitted_data_categories=data["permitted_data_categories"],
            permitted_purposes=data["permitted_purposes"],
            trusted_third_parties=data.get("trusted_third_parties", []),
            blocked_third_parties=data.get("blocked_third_parties", []),
            default_action=data.get("default_action", "ASK_ME"),
            strictness_level=data.get("strictness_level", 5),
            created_at=data.get("created_at", int(time.time())),
            updated_at=data.get("updated_at", int(time.time()))
        )

    def to_json(self) -> str:
        """Converts the PrivacyProfile object to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "PrivacyProfile":
        """Creates a PrivacyProfile object from a JSON string."""
        return cls.from_dict(json.loads(json_str))


class PrivacyProfileManager:
    """
    Manages creation, storage, and retrieval of user privacy profiles.
    """
    def __init__(self, storage_path: str = "user_profiles/"):
        """
        Initializes the PrivacyProfileManager.

        Args:
            storage_path (str): The directory path to store profile JSON files.
        """
        self.storage_path = storage_path
        self.active_profile: Optional[PrivacyProfile] = None
        self.profiles: Dict[str, PrivacyProfile] = {} # In-memory cache of profiles {profile_id: Profile}

        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        else:
            self._load_all_profiles_from_storage()

    def _get_profile_filepath(self, profile_id: str) -> str:
        """Generates the filepath for a given profile_id."""
        return os.path.join(self.storage_path, f"{profile_id}.json")

    def create_profile(self, user_id: str, profile_id: str, profile_name: str,
                       permitted_categories: Optional[List[DataCategory]] = None,
                       permitted_purposes: Optional[List[Purpose]] = None,
                       strictness: int = 5) -> PrivacyProfile:
        """
        Creates a new privacy profile.

        Args:
            user_id (str): The ID of the user.
            profile_id (str): A unique ID for the new profile.
            profile_name (str): A human-readable name for the profile.
            permitted_categories (Optional[List[DataCategory]]): List of data categories permitted.
            permitted_purposes (Optional[List[Purpose]]): List of purposes permitted.
            strictness (int): Strictness level.

        Returns:
            PrivacyProfile: The created profile.

        Raises:
            ValueError: If a profile with the given ID already exists.
        """
        if profile_id in self.profiles:
            raise ValueError(f"Profile with ID '{profile_id}' already exists.")

        profile = PrivacyProfile(
            profile_id=profile_id,
            profile_name=profile_name,
            user_id=user_id,
            permitted_data_categories=permitted_categories or [],
            permitted_purposes=permitted_purposes or [],
            strictness_level=strictness
        )
        self.profiles[profile_id] = profile
        self.save_profile(profile)
        return profile

    def save_profile(self, profile: PrivacyProfile) -> None:
        """
        Saves a privacy profile to a JSON file.

        Args:
            profile (PrivacyProfile): The profile to save.
        """
        filepath = self._get_profile_filepath(profile.profile_id)
        profile.updated_at = int(time.time()) # Update timestamp on save
        try:
            with open(filepath, 'w') as f:
                f.write(profile.to_json())
            self.profiles[profile.profile_id] = profile # Update cache
        except IOError as e:
            print(f"Error saving profile {profile.profile_id} to {filepath}: {e}")
            # Potentially re-raise or handle more gracefully

    def load_profile(self, profile_id: str) -> Optional[PrivacyProfile]:
        """
        Loads a privacy profile from a JSON file.

        Args:
            profile_id (str): The ID of the profile to load.

        Returns:
            Optional[PrivacyProfile]: The loaded profile, or None if not found or error.
        """
        if profile_id in self.profiles: # Check cache first
             return self.profiles[profile_id]

        filepath = self._get_profile_filepath(profile_id)
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r') as f:
                json_str = f.read()
                profile = PrivacyProfile.from_json(json_str)
                self.profiles[profile.profile_id] = profile # Cache it
                return profile
        except (IOError, json.JSONDecodeError, KeyError, ValueError) as e: # Catch potential errors during load/parse
            print(f"Error loading or parsing profile {profile_id} from {filepath}: {e}")
            if os.path.exists(filepath): # Optionally remove corrupted file
                 # os.remove(filepath) # Be careful with auto-deletion
                 pass
            return None

    def _load_all_profiles_from_storage(self) -> None:
        """Loads all profiles from the storage directory into the cache."""
        if not os.path.exists(self.storage_path):
            return
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                profile_id = filename[:-5] # Remove .json extension
                # Avoid reloading if already in cache (e.g. due to save_profile)
                if profile_id not in self.profiles:
                    self.load_profile(profile_id)
                    # load_profile handles caching and error reporting

    def set_active_profile(self, profile_id: str) -> bool:
        """
        Sets a profile as the active one for the current session/user.

        Args:
            profile_id (str): The ID of the profile to set as active.

        Returns:
            bool: True if the profile was successfully set as active, False otherwise.
        """
        profile = self.load_profile(profile_id)
        if profile:
            self.active_profile = profile
            return True
        return False

    def get_active_profile(self) -> Optional[PrivacyProfile]:
        """
        Returns the currently active profile.

        Returns:
            Optional[PrivacyProfile]: The active profile, or None if no profile is active.
        """
        return self.active_profile

    def get_profile(self, profile_id: str) -> Optional[PrivacyProfile]:
        """Retrieves a profile by its ID (loads if not in cache)."""
        return self.load_profile(profile_id)

    def list_profiles(self, user_id: Optional[str] = None) -> List[PrivacyProfile]:
        """
        Lists all available profiles, optionally filtered by user_id.
        Ensures all profiles from disk are loaded before listing.
        """
        self._load_all_profiles_from_storage() # Ensure cache is up-to-date
        if user_id:
            return [p for p in self.profiles.values() if p.user_id == user_id]
        return list(self.profiles.values())


if __name__ == '__main__':
    # Example Usage
    # Ensure privacy_framework is in PYTHONPATH or project is structured for imports

    # Create a manager (profiles will be stored in 'user_profiles/' subdirectory)
    profile_manager = PrivacyProfileManager(storage_path="user_profiles_example/")

    user1_id = "user_josephis_001"

    # Clean up previous example run if any
    if os.path.exists(profile_manager._get_profile_filepath("default_strict")):
        os.remove(profile_manager._get_profile_filepath("default_strict"))
    if os.path.exists(profile_manager._get_profile_filepath("balanced_share")):
        os.remove(profile_manager._get_profile_filepath("balanced_share"))

    # (Re-)Initialize manager to clear cache and load from (now empty) storage
    profile_manager = PrivacyProfileManager(storage_path="user_profiles_example/")


    print("--- Creating Profiles ---")
    try:
        strict_profile = profile_manager.create_profile(
            user_id=user1_id,
            profile_id="default_strict",
            profile_name="Default Strict",
            permitted_categories=[DataCategory.PERSONAL_INFO], # Only allow personal info for service delivery
            permitted_purposes=[Purpose.SERVICE_DELIVERY],
            strictness=9
        )
        print(f"Created profile: {strict_profile.profile_name} (ID: {strict_profile.profile_id})")

        balanced_profile = profile_manager.create_profile(
            user_id=user1_id,
            profile_id="balanced_share",
            profile_name="Balanced Sharing",
            permitted_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.DEVICE_INFO],
            permitted_purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS, Purpose.PERSONALIZATION],
            trusted_third_parties=["AnalyticsCorpInternal", "PersonalizationEnginePartner"],
            strictness=5
        )
        print(f"Created profile: {balanced_profile.profile_name} (ID: {balanced_profile.profile_id})")
    except ValueError as e:
        print(f"Error creating profile: {e}")


    print("\n--- Listing Profiles ---")
    all_profiles = profile_manager.list_profiles()
    if all_profiles:
        for p in all_profiles:
            print(f"- {p.profile_name} (ID: {p.profile_id}), User: {p.user_id}, Strictness: {p.strictness_level}")
    else:
        print("No profiles found.")

    print("\n--- Loading a Profile ---")
    loaded_profile = profile_manager.load_profile("default_strict")
    if loaded_profile:
        print(f"Loaded profile: {loaded_profile.profile_name}")
        print(f"  Permitted Data Categories: {[cat.name for cat in loaded_profile.permitted_data_categories]}")
        print(f"  Permitted Purposes: {[purp.name for purp in loaded_profile.permitted_purposes]}")
    else:
        print("Profile 'default_strict' not found after trying to load.")

    print("\n--- Setting Active Profile ---")
    if profile_manager.set_active_profile("default_strict"):
        active = profile_manager.get_active_profile()
        if active:
            print(f"Active profile set to: {active.profile_name}")
        else:
            print("Failed to retrieve active profile even after setting it.")
    else:
        print("Failed to set 'default_strict' as active.")

    print("\n--- Example of how a profile might generate a UserConsent (conceptual) ---")
    # This is a simplified conceptual link. Actual consent generation would be more complex.
    # and likely involve the ConsentManager.
    active_p = profile_manager.get_active_profile()
    if active_p:
        # Example policy details
        example_policy_id = "policy_xyz_123"
        example_policy_version = 1

        # Based on the active profile, decide what to consent to for *this specific policy*
        # This logic would be more sophisticated, comparing profile against policy details
        consented_categories = [cat for cat in active_p.permitted_data_categories if cat in [DataCategory.PERSONAL_INFO, DataCategory.DEVICE_INFO]] # Filter against policy's actual request
        consented_purposes = [purp for purp in active_p.permitted_purposes if purp in [Purpose.SERVICE_DELIVERY]]

        conceptual_consent = UserConsent(
            consent_id=f"consent_{user1_id}_{example_policy_id}_{int(time.time())}",
            user_id=user1_id,
            policy_id=example_policy_id,
            version=example_policy_version,
            data_categories_consented=consented_categories,
            purposes_consented=consented_purposes,
            third_parties_consented=active_p.trusted_third_parties # Simplified
        )
        print("Conceptual UserConsent generated from active profile:")
        # print(conceptual_consent.to_json()) # This will fail if UserConsent is not fully imported/defined
        print(f"  Consent ID: {conceptual_consent.consent_id}")
        print(f"  User ID: {conceptual_consent.user_id}")
        print(f"  Consented Categories: {[c.name for c in conceptual_consent.data_categories_consented]}")
        print(f"  Consented Purposes: {[p.name for p in conceptual_consent.purposes_consented]}")

    print(f"\nProfiles are stored in: {os.path.abspath(profile_manager.storage_path)}")
    print("Run this script again to see profiles being loaded from storage.")
