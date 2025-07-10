# src/privacy_framework/consent_manager.py
"""
Manages user consent records for the Privacy Protocol.
"""
import json # Added
import hashlib # Added
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
    Manages the storage, retrieval, and updating of UserConsent objects,
    delegating persistence to a ConsentStore.
    """

    def __init__(self, consent_store: 'ConsentStore'):
        """
        Initializes the ConsentManager.

        Args:
            consent_store (ConsentStore): An instance of ConsentStore for persistence.
        """
        if consent_store is None:
            raise ValueError("ConsentStore instance must be provided.")
        self.store = consent_store

    def grant_consent(self, consent: UserConsent) -> bool:
        """
        Grants/stores a new consent. If an active consent for the same user/policy
        already exists, this new one (if active and more recent) might supersede it
        based on ConsentStore's logic for loading the latest active one.

        Args:
            consent (UserConsent): The consent object to store.

        Returns:
            bool: True if consent was successfully saved by the store, False otherwise.
        """
        # TODO: Consider logic if a consent with the exact same consent_id already exists.
        # The store might overwrite or reject; current ConsentStore.save_consent overwrites.
        return self.store.save_consent(consent)

    def get_consent_by_id(self, user_id: str, consent_id: str) -> Optional[UserConsent]:
        """
        Retrieves a specific consent record by its ID for a given user.

        Args:
            user_id (str): The ID of the user.
            consent_id (str): The ID of the consent to retrieve.

        Returns:
            Optional[UserConsent]: The consent object if found, else None.
        """
        return self.store.load_consent(user_id=user_id, consent_id=consent_id)

    def get_active_consent(self, user_id: str, policy_id: str) -> Optional[UserConsent]:
        """
        Retrieves the most recent, active UserConsent for a specific user and policy
        by querying the ConsentStore.

        Args:
            user_id (str): The ID of the user.
            policy_id (str): The ID of the policy.

        Returns:
            Optional[UserConsent]: The active consent object if found, else None.
        """
        return self.store.load_latest_active_consent(user_id=user_id, policy_id=policy_id)

    def update_consent_details(self, user_id: str, consent_id: str,
                               data_categories_consented: Optional[List[DataCategory]] = None,
                               purposes_consented: Optional[List[Purpose]] = None,
                               third_parties_consented: Optional[List[str]] = None,
                               is_active: Optional[bool] = None,
                               obfuscation_preferences: Optional[Dict[str, str]] = None
                               ) -> Optional[UserConsent]:
        """
        Updates an existing consent record by loading, modifying, and re-saving it.
        The timestamp of the consent record is updated.

        Args:
            user_id (str): The ID of the user whose consent is being updated.
            consent_id (str): The ID of the consent to update.
            data_categories_consented (Optional[List[DataCategory]]): New list of consented data categories.
            purposes_consented (Optional[List[Purpose]]): New list of consented purposes.
            third_parties_consented (Optional[List[str]]): New list of consented third parties.
            is_active (Optional[bool]): New active status.
            obfuscation_preferences (Optional[Dict[str, str]]): New obfuscation preferences.

        Returns:
            Optional[UserConsent]: The updated consent object, or None if not found or save fails.
        """
        consent = self.store.load_consent(user_id=user_id, consent_id=consent_id)
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

        if self.store.save_consent(consent):
            return consent
        return None # Save failed

    def deactivate_consent(self, user_id: str, consent_id: str) -> Optional[UserConsent]:
        """
        Deactivates a consent record for a given user.

        Args:
            user_id (str): The ID of the user.
            consent_id (str): The ID of the consent to deactivate.

        Returns:
            Optional[UserConsent]: The deactivated consent object, or None if not found or save fails.
        """
        return self.update_consent_details(user_id=user_id, consent_id=consent_id, is_active=False)

    def sign_consent(self, user_id: str, consent_id: str, signature_service: Optional[Any] = None) -> Optional[UserConsent]:
        """
        Placeholder for cryptographically signing a UserConsent object.
        This conceptual method outlines how a consent record would be prepared for
        verifiable storage, potentially on a decentralized ledger (Consent Chain).

        Args:
            user_id (str): The ID of the user (e.g., a DID from DigiSocialBlock).
            consent_id (str): The ID of the consent to sign.
            signature_service (Optional[Any]): A conceptual external or integrated service
                                             (e.g., linked to user's wallet/identity in DigiSocialBlock)
                                             that can perform cryptographic signing.

        Returns:
            Optional[UserConsent]: The consent object with its `signature` field populated,
                                 or None if the consent is not found or saving fails.
        """
        # TODO: Integrate with DigiSocialBlock's identity/wallet for actual cryptographic signing.
        #       This would involve:
        #       1. Serializing the core consent details into a canonical format.
        #       2. The user (or their agent) signing this data using their private key.
        #          (e.g., `signed_data_hash = Transaction.Sign(user_private_key, hash_of_canonical_consent_data)`)
        #       3. Storing the signature in `consent.signature`.
        #       4. Optionally, anchoring the hash of the signed consent or the consent itself
        #          to a blockchain (e.g., EmPower1 or a dedicated Consent Chain via DigiSocialBlock)
        #          to create an immutable, verifiable, and timestamped record.
        #          (e.g., `ledger_tx_id = ConsentChain.recordConsent(consent_id, user_did, signed_consent_hash)`)
        #       Verification would then involve:
        #       1. Retrieving the signed consent.
        #       2. Re-serializing its core details.
        #       3. Using the user's public key (from DID) to verify the signature against the serialized data.
        #          (e.g., `isValid = VerifySignature(user_public_key, signature, hash_of_canonical_consent_data)`)
        #       4. Optionally, cross-referencing with the blockchain record.

        consent = self.store.load_consent(user_id=user_id, consent_id=consent_id)
        if not consent:
            return None

        # Conceptual: Create a stable string representation of what's being signed.
        # Important fields should be included. Order matters for consistent hashing if hash is signed.
        data_to_sign_parts = [
            consent.consent_id,
            consent.user_id,
            consent.policy_id,
            str(consent.version),
            str(consent.timestamp), # Original timestamp of granting/last significant update
            json.dumps(sorted([cat.value for cat in consent.data_categories_consented])),
            json.dumps(sorted([p.value for p in consent.purposes_consented])),
            json.dumps(sorted(consent.third_parties_consented)),
            str(consent.is_active)
        ]
        consent_data_to_sign = "|".join(data_to_sign_parts)

        if signature_service:
            # In a real system: conceptual_signature = signature_service.sign(consent_data_to_sign)
            # For now, just a placeholder indicating it was "signed"
            consent.signature = f"conceptually_signed_by_service({hashlib.sha256(consent_data_to_sign.encode()).hexdigest()[:16]})_at_{int(time.time())}"
        else:
            consent.signature = f"placeholder_signature_for_{consent_id}_datahash_{hashlib.sha256(consent_data_to_sign.encode()).hexdigest()[:8]}"

        # Signing might be considered an update to the consent record itself (adding the signature),
        # so updating the timestamp might be relevant. Or, the signature timestamp is separate.
        # For this conceptual step, let's assume signing also updates the record's timestamp.
        consent.timestamp = int(time.time())

        if self.store.save_consent(consent): # Re-store to save the signature and new timestamp
            return consent
        return None # Save failed

    def get_all_consents_for_user(self, user_id: str) -> List[UserConsent]:
        """
        Retrieves all consent records for a specific user from the ConsentStore.

        Args:
            user_id (str): The ID of the user.

        Returns:
            List[UserConsent]: A list of consent objects, sorted by timestamp descending by ConsentStore.
        """
        return self.store.load_all_consents_for_user(user_id=user_id)


if __name__ == '__main__':
    # Example Usage
    # This example will require a ConsentStore instance.
    # For standalone testing here, one might mock it or set up a temporary file-based one.

    # Assuming ConsentStore is available and a temp path can be used:
    from privacy_framework.consent_store import ConsentStore # Assuming it's in the same package level
    import shutil
    demo_store_path = "_app_data_demo/consent_manager_test_consents/"
    if os.path.exists(demo_store_path):
        shutil.rmtree(demo_store_path) # Clean up from previous runs

    temp_consent_store = ConsentStore(storage_path=demo_store_path)
    manager = ConsentManager(consent_store=temp_consent_store)

    # Create a sample consent
    consent1_id = f"consent_user1_policyA_v1_{int(time.time())}"
    # Assuming UserConsent, DataCategory, Purpose are correctly importable
    # (e.g., by running from project root or having src in PYTHONPATH)

    # manager = ConsentManager() # This would fail as ConsentStore is required.
    # The following example code is now illustrative of how one might use it
    # if a ConsentStore instance (e.g., temp_consent_store) was provided.

    # # Create a sample consent
    # consent1_id = f"consent_user1_policyA_v1_{int(time.time())}"
    # consent1 = UserConsent(
    #     consent_id=consent1_id,
    #     user_id="user123",
    #     policy_id="policyA_v1",
    #     version=1,
    #     data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
    #     purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
    #     third_parties_consented=["analytics.example.com"],
    #     is_active=True
    # )
    # manager.grant_consent(consent1) # Assuming manager is initialized with a store
    # print(f"Stored consent: {consent1_id}")

    # retrieved_consent = manager.get_consent_by_id(user_id="user123", consent_id=consent1_id)
    # if retrieved_consent:
    #     print(f"Retrieved consent by ID: {retrieved_consent.consent_id}, Active: {retrieved_consent.is_active}")

    # active_consent = manager.get_active_consent(user_id="user123", policy_id="policyA_v1")
    # if active_consent:
    #     print(f"Active consent for user123/policyA_v1: {active_consent.consent_id}")
    # else:
    #     print("No active consent found for user123/policyA_v1.")

    # # Update consent
    # time.sleep(1) # ensure timestamp changes
    # updated_consent = manager.update_consent_details(
    #     user_id="user123",
    #     consent_id=consent1_id,
    #     purposes_consented=[Purpose.SERVICE_DELIVERY], # User revokes consent for ANALYTICS
    #     is_active=True
    # )
    # if updated_consent:
    #     print(f"Updated consent: {updated_consent.consent_id}, Purposes: {[p.name for p in updated_consent.purposes_consented]}")
    #     active_after_update = manager.get_active_consent(user_id="user123", policy_id="policyA_v1")
    #     if active_after_update:
    #          print(f"Active consent purposes after update: {[p.name for p in active_after_update.purposes_consented]}")


    # # Sign consent (placeholder)
    # signed_consent = manager.sign_consent(user_id="user123", consent_id=consent1_id)
    # if signed_consent:
    #     print(f"Signed consent: {signed_consent.consent_id}, Signature: {signed_consent.signature}")

    # # Deactivate consent
    # time.sleep(1)
    # deactivated_consent = manager.deactivate_consent(user_id="user123", consent_id=consent1_id)
    # if deactivated_consent:
    #     print(f"Deactivated consent: {deactivated_consent.consent_id}, Active: {deactivated_consent.is_active}")

    # active_after_deactivation = manager.get_active_consent(user_id="user123", policy_id="policyA_v1")
    # if active_after_deactivation:
    #     print(f"Active consent for user123/policyA_v1 after deactivation: {active_after_deactivation.consent_id}")
    # else:
    #     print("No active consent found for user123/policyA_v1 after deactivation (as expected).")

    # # Example of storing another consent for the same user/policy (simulating history)
    # consent2_id = f"consent_user1_policyA_v1_older_{int(time.time())-1000}" # older timestamp
    # consent2 = UserConsent(
    #     consent_id=consent2_id,
    #     user_id="user123",
    #     policy_id="policyA_v1",
    #     version=1,
    #     data_categories_consented=[DataCategory.PERSONAL_INFO],
    #     purposes_consented=[Purpose.SERVICE_DELIVERY],
    #     third_parties_consented=[],
    #     is_active=True, # Mark as active, but it's older
    #     timestamp=int(time.time())-10000 # ensure it's older
    # )
    # manager.grant_consent(consent2)
    # print(f"Stored older (but active) consent: {consent2.consent_id}")

    # # Create a new active consent to supersede the older one
    # consent3_id = f"consent_user1_policyA_v1_newest_{int(time.time())}"
    # consent3 = UserConsent(
    #     consent_id=consent3_id,
    #     user_id="user123",
    #     policy_id="policyA_v1",
    #     version=1,
    #     data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.DEVICE_INFO],
    #     purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.SECURITY],
    #     third_parties_consented=[],
    #     is_active=True,
    #     timestamp=int(time.time())
    # )
    # manager.grant_consent(consent3)
    # print(f"Stored newest active consent: {consent3.consent_id}")

    # final_active = manager.get_active_consent(user_id="user123", policy_id="policyA_v1")
    # if final_active:
    #     print(f"Final active consent for user123/policyA_v1: {final_active.consent_id} (should be newest one)")
    #     print(f"  Purposes: {[p.name for p in final_active.purposes_consented]}")
    # else:
    #     print("Error: No active consent found when one was expected.")

    # all_user_consents = manager.get_all_consents_for_user("user123")
    # print(f"\nAll consents for user123 (sorted by time desc):")
    # for c in all_user_consents:
    #     print(f"  ID: {c.consent_id}, Active: {c.is_active}, Timestamp: {c.timestamp}")
    pass # Keep the if __name__ block, but comment out the old example code
