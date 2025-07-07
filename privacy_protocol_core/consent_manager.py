from collections import defaultdict
from datetime import datetime, timezone
import uuid

import hashlib # Added for more realistic placeholder signature content

try:
    from .consent import UserConsent
    from .policy import PrivacyPolicy # Might be needed for type hinting or context
    from .consent_store import ConsentStore
except ImportError: # For standalone testing if needed
    from consent import UserConsent
    from policy import PrivacyPolicy
    from consent_store import ConsentStore


class ConsentManager:
    def __init__(self, consent_store: ConsentStore):
        """
        Initializes the ConsentManager.
        Manages user consent records, using a ConsentStore for persistence.
        """
        if not isinstance(consent_store, ConsentStore):
            raise TypeError("consent_store must be an instance of ConsentStore.")
        self.store = consent_store

    def add_consent(self, consent: UserConsent) -> UserConsent:
        """
        Adds a new consent record. If this new consent is active,
        it ensures other active consents for the same user/policy are
        appropriately handled (e.g., marked inactive if older or overlapping).
        """
        if not isinstance(consent, UserConsent):
            raise ValueError("Invalid consent object provided.")
        if not consent.user_id or not consent.policy_id or not consent.consent_id:
            raise ValueError("User ID, Policy ID, and Consent ID must be set in the consent object.")

        if consent.is_active:
            existing_consents = self.store.load_consents_for_user_policy(consent.user_id, consent.policy_id)
            for ec in existing_consents:
                if ec.is_active and ec.consent_id != consent.consent_id:
                    if consent.timestamp >= ec.timestamp:
                        ec.is_active = False
                        self.store.save_consent(ec)

        if self.store.save_consent(consent):
            return consent
        else:
            raise Exception(f"Failed to save consent {consent.consent_id} to store.")


    def get_active_consent(self, user_id: str, policy_id: str) -> UserConsent | None:
        """
        Retrieves the most recent, active, and non-expired consent for a given user and policy
        directly from the ConsentStore.
        """
        return self.store.load_latest_active_consent(user_id, policy_id)

    def revoke_consent(self, user_id: str, policy_id: str, consent_id: str = None) -> bool:
        """
        Revokes consent.
        If consent_id is provided, revokes that specific record.
        Otherwise, revokes the current active consent for the user_id/policy_id pair.
        Saves the change to the ConsentStore.
        Returns True if a consent was successfully revoked and saved, False otherwise.
        """
        consent_to_revoke = None
        if consent_id:
            history = self.store.load_consents_for_user_policy(user_id, policy_id)
            for c in history:
                if c.consent_id == consent_id:
                    consent_to_revoke = c
                    break
            if consent_to_revoke and (consent_to_revoke.user_id != user_id or consent_to_revoke.policy_id != policy_id):
                return False # Mismatch
        else:
            consent_to_revoke = self.get_active_consent(user_id, policy_id)

        if consent_to_revoke and consent_to_revoke.is_active:
            consent_to_revoke.is_active = False
            return self.store.save_consent(consent_to_revoke)
        elif consent_to_revoke and not consent_to_revoke.is_active:
            return True

        return False

    def get_consent_history(self, user_id: str, policy_id: str) -> list[UserConsent]:
        """
        Retrieves all consent versions (active and inactive) for a user and policy
        from the ConsentStore, ordered by timestamp (most recent first).
        """
        return self.store.load_consents_for_user_policy(user_id, policy_id)

    def get_consent_by_id(self, user_id: str, policy_id: str, consent_id: str) -> UserConsent | None:
        """
        Retrieves a specific consent record by its ID for a given user/policy.
        Loads history and filters.
        """
        history = self.store.load_consents_for_user_policy(user_id, policy_id)
        for consent_record in history:
            if consent_record.consent_id == consent_id:
                return consent_record
        return None

    def sign_consent(self, consent: UserConsent) -> UserConsent:
        """
        Placeholder for cryptographically signing a consent object.

        Conceptual Link: DigiSocialBlock & EmPower1 Blockchain.
        In a real implementation, this would involve:
        1. User's private key (managed by a wallet system, e.g., linked to DigiSocialBlock identity).
        2. Creating a canonical representation of the consent data (e.g., sorted JSON string).
        3. Signing the hash of this canonical data using the user's private key (e.g., ECDSA).
           Ref: DigiSocialBlock `pkg/identity/identity.go` (Sign) and `pkg/ledger/transaction.go` (Sign method for transactions which implies signing arbitrary data).
        4. Storing the generated signature in `consent.signature`.
        5. Optionally, the signed consent (or its hash and signature) could be recorded on a
           decentralized ledger (e.g., EmPower1 or a dedicated "Consent Chain") for immutable,
           verifiable proof of consent at a specific time. This would involve creating a transaction.

        The current implementation is a simple placeholder.
        """
        # Simulate hashing key parts of consent for a more realistic placeholder sig content
        consent_details_for_hash = (
            f"{consent.user_id}:{consent.policy_id}:{consent.policy_version}:"
            f"{','.join(sorted([dc.value for dc in consent.data_categories_consented]))}:"
            f"{','.join(sorted([p.value for p in consent.purposes_consented]))}:"
            f"{consent.timestamp}:{consent.is_active}:{consent.expires_at or ''}"
        )
        hashed_details = hashlib.sha256(consent_details_for_hash.encode('utf-8')).hexdigest()[:16] # Short hash for placeholder

        consent.signature = f"signed_placeholder_{uuid.uuid4()}_{hashed_details}"

        # In a real scenario, would also save this updated consent (with signature) to the store.
        # self.store.save_consent(consent)
        print(f"Placeholder: Consent {consent.consent_id} signed with '{consent.signature}'.")
        return consent

    def verify_consent_signature(self, consent: UserConsent) -> bool:
        """
        Placeholder for verifying the cryptographic signature of a consent object.

        Conceptual Link: DigiSocialBlock & EmPower1 Blockchain.
        This would involve:
        1. Retrieving the user's public key (associated with their DigiSocialBlock identity).
        2. Re-creating the same canonical representation of consent data that was signed.
        3. Using the public key and the signature from `consent.signature` to verify the signature
           against the hash of the canonical data.
           Ref: DigiSocialBlock `pkg/identity/identity.go` (VerifySignature).
        4. If integrated with a "Consent Chain", this might also involve checking the transaction
           on the ledger that recorded this consent.

        The current implementation is a simple placeholder check.
        """
        if consent.signature and consent.signature.startswith("signed_placeholder_"):
            # Conceptual: could try to re-calculate the dummy hash and check if it's in the sig
            print(f"Placeholder: Signature for consent {consent.consent_id} is conceptually valid (placeholder check).")
            return True
        print(f"Placeholder: Signature for consent {consent.consent_id} is invalid or missing.")
        return False

if __name__ == '__main__':
    from policy import DataCategory, Purpose
    # ConsentStore is already imported correctly at the top for standalone execution
    import tempfile
    import shutil
    from datetime import timedelta

    temp_dir_manager_tests = tempfile.mkdtemp()
    print(f"Using temporary directory for ConsentManager tests: {temp_dir_manager_tests}")
    test_consent_store = ConsentStore(base_path=temp_dir_manager_tests)
    manager = ConsentManager(consent_store=test_consent_store)

    user1_id = "userTest1"
    policyA_id = "PolicyTestA"
    ts_now = datetime.now(timezone.utc)

    consent1_v1 = UserConsent(
        user_id=user1_id, policy_id=policyA_id, policy_version="1.0",
        data_categories_consented=[DataCategory.PERSONAL_INFO],
        purposes_consented=[Purpose.SERVICE_DELIVERY],
        timestamp=(ts_now - timedelta(days=2)).isoformat()
    )
    manager.add_consent(consent1_v1)
    manager.sign_consent(consent1_v1)

    consent2_v1_1_active_expiring = UserConsent(
        user_id=user1_id, policy_id=policyA_id, policy_version="1.1",
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
        timestamp=(ts_now - timedelta(days=1)).isoformat(),
        expires_at=(ts_now + timedelta(minutes=1)).isoformat()
    )
    manager.add_consent(consent2_v1_1_active_expiring)

    print("--- Initial State ---")
    active_c = manager.get_active_consent(user1_id, policyA_id)
    print(f"{user1_id}, {policyA_id} active consent: Version {active_c.policy_version if active_c else 'None'}")
    assert active_c and active_c.consent_id == consent2_v1_1_active_expiring.consent_id

    history_after_add = manager.get_consent_history(user1_id, policyA_id)
    consent1_v1_from_store = next((c for c in history_after_add if c.consent_id == consent1_v1.consent_id), None)
    assert consent1_v1_from_store and not consent1_v1_from_store.is_active, "Older consent should be inactive in store."

    print(f"\n--- Testing Expiration of {consent2_v1_1_active_expiring.consent_id} ---")
    consent2_v1_1_active_expiring.expires_at = (ts_now - timedelta(seconds=10)).isoformat()
    consent2_v1_1_active_expiring.is_active = True
    manager.store.save_consent(consent2_v1_1_active_expiring)

    active_c_after_expiry = manager.get_active_consent(user1_id, policyA_id)
    print(f"{user1_id}, {policyA_id} active consent after v1.1 expired: {active_c_after_expiry.policy_version if active_c_after_expiry else 'None'}")
    assert active_c_after_expiry is None

    consent1_v1.is_active = True
    consent1_v1.timestamp = (ts_now - timedelta(minutes=5)).isoformat()
    manager.add_consent(consent1_v1)

    print("\n--- Revoking Consent ---")
    active_before_revoke = manager.get_active_consent(user1_id, policyA_id)
    assert active_before_revoke and active_before_revoke.consent_id == consent1_v1.consent_id
    print(f"Active consent before revoke: {active_before_revoke.consent_id}")

    manager.revoke_consent(user_id=user1_id, policy_id=policyA_id, consent_id=consent1_v1.consent_id)
    active_after_revoke = manager.get_active_consent(user1_id, policyA_id)
    print(f"{user1_id}, {policyA_id} active consent after specific revoke: {active_after_revoke.policy_version if active_after_revoke else 'None'}")
    assert active_after_revoke is None

    consent3_v1_2_active = UserConsent(
        user_id=user1_id, policy_id=policyA_id, policy_version="1.2",
        timestamp=ts_now.isoformat()
    )
    manager.add_consent(consent3_v1_2_active)
    print(f"Revoking latest active consent for {user1_id}, {policyA_id} (which is {consent3_v1_2_active.consent_id})")
    manager.revoke_consent(user_id=user1_id, policy_id=policyA_id)
    active_after_latest_revoke = manager.get_active_consent(user1_id, policyA_id)
    assert active_after_latest_revoke is None

    print("\n--- Consent History ---")
    history = manager.get_consent_history(user1_id, policyA_id)
    print(f"{user1_id}, {policyA_id} consent history (count: {len(history)}):")
    for c_hist in history:
        print(f"  ID: {c_hist.consent_id}, Ver: {c_hist.policy_version}, Active: {c_hist.is_active}, TS: {c_hist.timestamp}")
    assert len(history) == 3
    assert not history[0].is_active
    assert not history[1].is_active
    assert not history[2].is_active

    print("\n--- Get by ID (specific user/policy context) ---")
    retrieved_by_id = manager.get_consent_by_id(user_id=user1_id, policy_id=policyA_id, consent_id=consent1_v1.consent_id)
    print(f"Retrieved consent by ID ({consent1_v1.consent_id}): Policy {retrieved_by_id.policy_id if retrieved_by_id else 'Not Found'}")
    assert retrieved_by_id and retrieved_by_id.policy_id == policyA_id

    try:
        shutil.rmtree(temp_dir_manager_tests)
        print(f"\nCleaned up temporary directory: {temp_dir_manager_tests}")
    except Exception as e:
        print(f"Error cleaning up temp directory {temp_dir_manager_tests}: {e}")

    print("\nAll ConsentManager examples with ConsentStore executed.")
