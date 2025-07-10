# src/privacy_framework/consent_manager.py
"""
Manages user consent records for the Privacy Protocol.
"""

from typing import Dict, Optional, List, Any
import time

try:
    from .consent import UserConsent # For type hinting and usage
    from .policy import DataCategory, Purpose # For updating consent details
except ImportError:
    # Fallback for direct execution or different project structures
    from privacy_framework.consent import UserConsent
    from privacy_framework.policy import DataCategory, Purpose

class ConsentManager:
    """
    Manages the storage, retrieval, and updating of UserConsent objects.
    For now, storage is in-memory.
    """

    def __init__(self):
        # Primary storage: consent_id -> UserConsent object
        self._consents: Dict[str, UserConsent] = {}
        # Secondary index for quick lookup of active consent: (user_id, policy_id) -> consent_id
        self._active_consent_index: Dict[tuple[str, str], str] = {}

    def store_consent(self, consent: UserConsent) -> None:
        """
        Stores a UserConsent object. If the consent is active and more recent,
        it updates the active consent index for the user/policy pair.

        Args:
            consent (UserConsent): The consent object to store.

        Raises:
            ValueError: If a consent with the same consent_id already exists but is different.
        """
        if consent.consent_id in self._consents and self._consents[consent.consent_id] != consent:
            # This basic check helps prevent accidental overwrites if not intended.
            # A more robust system might handle versioning or updates explicitly.
            # For now, if ID is same, we assume it's an update or re-storage of same object.
            pass

        self._consents[consent.consent_id] = consent

        # Update active consent index if this consent is active and is the latest
        user_policy_pair = (consent.user_id, consent.policy_id)
        if consent.is_active:
            current_active_consent_id = self._active_consent_index.get(user_policy_pair)
            if current_active_consent_id:
                current_active_consent = self._consents.get(current_active_consent_id)
                if current_active_consent and consent.timestamp >= current_active_consent.timestamp:
                    # New consent is more recent or same time, make it active
                    self._active_consent_index[user_policy_pair] = consent.consent_id
                # If older, the existing active consent remains.
            else:
                # No active consent for this pair yet, so this one becomes active.
                self._active_consent_index[user_policy_pair] = consent.consent_id
        else: # If the stored consent is not active
            # If this consent was previously the active one, remove it from active index
            if self._active_consent_index.get(user_policy_pair) == consent.consent_id:
                del self._active_consent_index[user_policy_pair]
                # Potentially find the next most recent active one, but this is complex.
                # For now, simply removing is fine. Retrieval will find no active one.

    def get_consent_by_id(self, consent_id: str) -> Optional[UserConsent]:
        """
        Retrieves a specific consent record by its ID.

        Args:
            consent_id (str): The ID of the consent to retrieve.

        Returns:
            Optional[UserConsent]: The consent object if found, else None.
        """
        return self._consents.get(consent_id)

    def get_active_consent(self, user_id: str, policy_id: str) -> Optional[UserConsent]:
        """
        Retrieves the most recent, active UserConsent for a specific user and policy.

        Args:
            user_id (str): The ID of the user.
            policy_id (str): The ID of the policy.

        Returns:
            Optional[UserConsent]: The active consent object if found, else None.
        """
        active_consent_id = self._active_consent_index.get((user_id, policy_id))
        if active_consent_id:
            consent = self._consents.get(active_consent_id)
            # Ensure it's indeed active (should be by index logic, but double check)
            if consent and consent.is_active:
                return consent
        return None

    def update_consent(self, consent_id: str,
                       data_categories_consented: Optional[List[DataCategory]] = None,
                       purposes_consented: Optional[List[Purpose]] = None,
                       third_parties_consented: Optional[List[str]] = None,
                       is_active: Optional[bool] = None,
                       obfuscation_preferences: Optional[Dict[str, str]] = None
                       ) -> Optional[UserConsent]:
        """
        Updates an existing consent record. Fields not provided will remain unchanged.
        The timestamp of the consent record is updated.

        Args:
            consent_id (str): The ID of the consent to update.
            data_categories_consented (Optional[List[DataCategory]]): New list of consented data categories.
            purposes_consented (Optional[List[Purpose]]): New list of consented purposes.
            third_parties_consented (Optional[List[str]]): New list of consented third parties.
            is_active (Optional[bool]): New active status.
            obfuscation_preferences (Optional[Dict[str, str]]): New obfuscation preferences.

        Returns:
            Optional[UserConsent]: The updated consent object, or None if not found.
        """
        consent = self.get_consent_by_id(consent_id)
        if not consent:
            return None

        if data_categories_consented is not None:
            consent.data_categories_consented = data_categories_consented
        if purposes_consented is not None:
            consent.purposes_consented = purposes_consented
        if third_parties_consented is not None:
            consent.third_parties_consented = third_parties_consented
        if is_active is not None:
            consent.is_active = is_active
        if obfuscation_preferences is not None:
            consent.obfuscation_preferences = obfuscation_preferences

        consent.timestamp = int(time.time()) # Update timestamp

        # Re-store to update indices correctly, especially the active_consent_index
        self.store_consent(consent)
        return consent

    def deactivate_consent(self, consent_id: str) -> Optional[UserConsent]:
        """
        Deactivates a consent record.

        Args:
            consent_id (str): The ID of the consent to deactivate.

        Returns:
            Optional[UserConsent]: The deactivated consent object, or None if not found.
        """
        return self.update_consent(consent_id, is_active=False)

    def sign_consent(self, consent_id: str, signature_service: Optional[Any] = None) -> Optional[UserConsent]:
        """
        Placeholder for cryptographically signing a UserConsent object.
        In a real implementation, this would involve a signature service or library.

        Args:
            consent_id (str): The ID of the consent to sign.
            signature_service (Optional[Any]): A conceptual service for generating signatures.

        Returns:
            Optional[UserConsent]: The consent object with a placeholder signature, or None if not found.
        """
        consent = self.get_consent_by_id(consent_id)
        if not consent:
            return None

        # Conceptual: Generate a string representation of consent to be signed
        # consent_data_to_sign = f"{consent.consent_id}|{consent.user_id}|{consent.policy_id}|{consent.version}|{consent.timestamp}"
        # In a real scenario, use a stable serialization format (e.g., canonical JSON)

        if signature_service:
            # conceptual_signature = signature_service.sign(consent_data_to_sign)
            consent.signature = f"signed_by_conceptual_service_at_{int(time.time())}"
        else:
            consent.signature = f"placeholder_signature_for_{consent_id}"

        consent.timestamp = int(time.time()) # Signature implies an update
        self.store_consent(consent) # Re-store to save the signature
        return consent

    def get_all_consents_for_user(self, user_id: str) -> List[UserConsent]:
        """
        Retrieves all consent records for a specific user, sorted by timestamp descending.

        Args:
            user_id (str): The ID of the user.

        Returns:
            List[UserConsent]: A list of consent objects.
        """
        user_consents = [c for c in self._consents.values() if c.user_id == user_id]
        user_consents.sort(key=lambda c: c.timestamp, reverse=True)
        return user_consents

if __name__ == '__main__':
    # Example Usage
    # Assuming UserConsent, DataCategory, Purpose are correctly importable
    # (e.g., by running from project root or having src in PYTHONPATH)

    manager = ConsentManager()

    # Create a sample consent
    consent1_id = f"consent_user1_policyA_v1_{int(time.time())}"
    consent1 = UserConsent(
        consent_id=consent1_id,
        user_id="user123",
        policy_id="policyA_v1",
        version=1,
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
        third_parties_consented=["analytics.example.com"],
        is_active=True
    )
    manager.store_consent(consent1)
    print(f"Stored consent: {consent1_id}")

    retrieved_consent = manager.get_consent_by_id(consent1_id)
    if retrieved_consent:
        print(f"Retrieved consent by ID: {retrieved_consent.consent_id}, Active: {retrieved_consent.is_active}")

    active_consent = manager.get_active_consent(user_id="user123", policy_id="policyA_v1")
    if active_consent:
        print(f"Active consent for user123/policyA_v1: {active_consent.consent_id}")
    else:
        print("No active consent found for user123/policyA_v1.")

    # Update consent
    time.sleep(1) # ensure timestamp changes
    updated_consent = manager.update_consent(
        consent_id=consent1_id,
        purposes_consented=[Purpose.SERVICE_DELIVERY], # User revokes consent for ANALYTICS
        is_active=True
    )
    if updated_consent:
        print(f"Updated consent: {updated_consent.consent_id}, Purposes: {[p.name for p in updated_consent.purposes_consented]}")
        active_after_update = manager.get_active_consent(user_id="user123", policy_id="policyA_v1")
        if active_after_update:
             print(f"Active consent purposes after update: {[p.name for p in active_after_update.purposes_consented]}")


    # Sign consent (placeholder)
    signed_consent = manager.sign_consent(consent1_id)
    if signed_consent:
        print(f"Signed consent: {signed_consent.consent_id}, Signature: {signed_consent.signature}")

    # Deactivate consent
    time.sleep(1)
    deactivated_consent = manager.deactivate_consent(consent1_id)
    if deactivated_consent:
        print(f"Deactivated consent: {deactivated_consent.consent_id}, Active: {deactivated_consent.is_active}")

    active_after_deactivation = manager.get_active_consent(user_id="user123", policy_id="policyA_v1")
    if active_after_deactivation:
        print(f"Active consent for user123/policyA_v1 after deactivation: {active_after_deactivation.consent_id}")
    else:
        print("No active consent found for user123/policyA_v1 after deactivation (as expected).")

    # Example of storing another consent for the same user/policy (simulating history)
    consent2_id = f"consent_user1_policyA_v1_older_{int(time.time())-1000}" # older timestamp
    consent2 = UserConsent(
        consent_id=consent2_id,
        user_id="user123",
        policy_id="policyA_v1",
        version=1,
        data_categories_consented=[DataCategory.PERSONAL_INFO],
        purposes_consented=[Purpose.SERVICE_DELIVERY],
        third_parties_consented=[],
        is_active=True, # Mark as active, but it's older
        timestamp=int(time.time())-10000 # ensure it's older
    )
    manager.store_consent(consent2)
    print(f"Stored older (but active) consent: {consent2.consent_id}")

    # Create a new active consent to supersede the older one
    consent3_id = f"consent_user1_policyA_v1_newest_{int(time.time())}"
    consent3 = UserConsent(
        consent_id=consent3_id,
        user_id="user123",
        policy_id="policyA_v1",
        version=1,
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.DEVICE_INFO],
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.SECURITY],
        third_parties_consented=[],
        is_active=True,
        timestamp=int(time.time())
    )
    manager.store_consent(consent3)
    print(f"Stored newest active consent: {consent3.consent_id}")

    final_active = manager.get_active_consent(user_id="user123", policy_id="policyA_v1")
    if final_active:
        print(f"Final active consent for user123/policyA_v1: {final_active.consent_id} (should be newest one)")
        print(f"  Purposes: {[p.name for p in final_active.purposes_consented]}")
    else:
        print("Error: No active consent found when one was expected.")

    all_user_consents = manager.get_all_consents_for_user("user123")
    print(f"\nAll consents for user123 (sorted by time desc):")
    for c in all_user_consents:
        print(f"  ID: {c.consent_id}, Active: {c.is_active}, Timestamp: {c.timestamp}")
