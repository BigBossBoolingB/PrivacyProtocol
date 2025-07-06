from collections import defaultdict
from datetime import datetime, timezone # Added timezone
import uuid # Added uuid

try:
    # Assuming UserConsent is in .consent and PrivacyPolicy in .policy
    from .consent import UserConsent
    from .policy import PrivacyPolicy # Might be needed for type hinting or context
except ImportError: # For standalone testing if needed
    from consent import UserConsent
    from policy import PrivacyPolicy


class ConsentManager:
    def __init__(self):
        """
        Initializes the ConsentManager.
        Manages user consent records, typically an in-memory store for this implementation.
        Structure of self.consents:
        {
            user_id_1: {
                policy_id_1: [UserConsent_v1, UserConsent_v2, ...], # List ordered by timestamp
                policy_id_2: [...],
            },
            user_id_2: {...}
        }
        """
        self._consents_by_user_policy = defaultdict(lambda: defaultdict(list))
        self._consents_by_id = {} # Direct access by consent_id: consent_id -> UserConsent

    def add_consent(self, consent: UserConsent):
        """
        Adds a new consent record or updates an existing one if consent_id matches.
        If a new consent for a user/policy makes a previous one outdated,
        it's recommended to manage active status explicitly or rely on latest timestamp.
        For simplicity, this version adds to a list, sorted by timestamp later.
        """
        if not isinstance(consent, UserConsent):
            raise ValueError("Invalid consent object provided.")
        if not consent.user_id or not consent.policy_id:
            raise ValueError("User ID and Policy ID must be set in the consent object.")

        # Deactivate older consents for the same user/policy if this new one is active
        if consent.is_active:
            active_consents = self._consents_by_user_policy[consent.user_id][consent.policy_id]
            for existing_consent in active_consents:
                if existing_consent.is_active and existing_consent.consent_id != consent.consent_id:
                    # Heuristic: if timestamps are very close and IDs differ, it might be an update
                    # For now, simple deactivation of other active consents for same user/policy.
                    if consent.timestamp >= existing_consent.timestamp :
                         existing_consent.is_active = False


        user_policy_consents = self._consents_by_user_policy[consent.user_id][consent.policy_id]

        # Check if this specific consent_id already exists to update it
        updated = False
        for i, existing_c in enumerate(user_policy_consents):
            if existing_c.consent_id == consent.consent_id:
                user_policy_consents[i] = consent
                updated = True
                break
        if not updated:
            user_policy_consents.append(consent)

        # Sort by timestamp, most recent first, to make get_active_consent simpler
        user_policy_consents.sort(key=lambda c: c.timestamp, reverse=True)

        self._consents_by_id[consent.consent_id] = consent
        return consent

    def get_active_consent(self, user_id: str, policy_id: str) -> UserConsent | None:
        """
        Retrieves the most recent, active consent for a given user and policy.
        """
        if user_id in self._consents_by_user_policy and policy_id in self._consents_by_user_policy[user_id]:
            user_policy_consents = self._consents_by_user_policy[user_id][policy_id]
            for consent_record in user_policy_consents: # Already sorted, newest first
                if consent_record.is_active:
                    # Check for expiration
                    if consent_record.expires_at:
                        try:
                            # Ensure the stored expires_at is parsed correctly, handling potential 'Z' for UTC
                            if consent_record.expires_at.endswith('Z'):
                                expiration_date = datetime.fromisoformat(consent_record.expires_at[:-1] + '+00:00')
                            else:
                                expiration_date = datetime.fromisoformat(consent_record.expires_at)

                            # Ensure current time is also timezone-aware (UTC) for comparison
                            current_time_utc = datetime.now(timezone.utc) # Corrected: use imported timezone

                            # If expiration_date is naive, make it aware (assume UTC if Z was present or no tz info)
                            if expiration_date.tzinfo is None:
                                expiration_date = expiration_date.replace(tzinfo=timezone.utc)

                            if expiration_date < current_time_utc:
                                consent_record.is_active = False # Mark as inactive
                                continue # Skip this expired consent
                        except ValueError: # Invalid date format in expires_at
                            pass # Treat as non-expiring or handle error
                    return consent_record
        return None

    def revoke_consent(self, user_id: str, policy_id: str, consent_id: str = None) -> bool:
        """
        Revokes consent.
        If consent_id is provided, revokes that specific record.
        Otherwise, revokes the current active consent for the user_id/policy_id pair.
        Returns True if a consent was successfully revoked, False otherwise.
        """
        revoked = False
        if consent_id:
            if consent_id in self._consents_by_id:
                consent_to_revoke = self._consents_by_id[consent_id]
                if consent_to_revoke.user_id == user_id and consent_to_revoke.policy_id == policy_id:
                    consent_to_revoke.is_active = False
                    # Update timestamp or add revocation specific timestamp if needed
                    # consent_to_revoke.timestamp = datetime.utcnow().isoformat()
                    revoked = True
        else: # Revoke the latest active one for user/policy
            active_consent = self.get_active_consent(user_id, policy_id)
            if active_consent:
                active_consent.is_active = False
                # active_consent.timestamp = datetime.utcnow().isoformat()
                revoked = True
        return revoked

    def get_consent_history(self, user_id: str, policy_id: str) -> list[UserConsent]:
        """
        Retrieves all consent versions (active and inactive) for a user and policy,
        ordered by timestamp (most recent first).
        """
        if user_id in self._consents_by_user_policy and policy_id in self._consents_by_user_policy[user_id]:
            # The list is already sorted by add_consent
            return list(self._consents_by_user_policy[user_id][policy_id])
        return []

    def get_consent_by_id(self, consent_id: str) -> UserConsent | None:
        """Retrieves a specific consent record by its ID."""
        return self._consents_by_id.get(consent_id)

    # --- Placeholder Verifiable Consent Methods ---
    def sign_consent(self, consent: UserConsent) -> UserConsent:
        """
        Placeholder for cryptographically signing a consent object.
        In a real implementation, this would involve private keys, possibly
        linking to a user's digital identity (e.g., DigiSocialBlock wallet).
        """
        # Conceptual: Generate a hash of key consent details, sign with user's private key.
        # Store the signature in consent.signature.
        consent.signature = f"signed_placeholder_{uuid.uuid4()}"
        print(f"Placeholder: Consent {consent.consent_id} signed with '{consent.signature}'.")
        return consent

    def verify_consent_signature(self, consent: UserConsent) -> bool:
        """
        Placeholder for verifying the cryptographic signature of a consent object.
        """
        if consent.signature and consent.signature.startswith("signed_placeholder_"):
            print(f"Placeholder: Signature for consent {consent.consent_id} is conceptually valid.")
            return True
        print(f"Placeholder: Signature for consent {consent.consent_id} is invalid or missing.")
        return False


if __name__ == '__main__':
    from policy import DataCategory, Purpose # For example usage

    manager = ConsentManager()

    # Create some consents
    consent1_user1_policyA_v1 = UserConsent(
        user_id="user1", policy_id="PolicyA", policy_version="1.0",
        data_categories_consented=[DataCategory.PERSONAL_INFO],
        purposes_consented=[Purpose.SERVICE_DELIVERY],
        timestamp=(datetime.utcnow() - timedelta(days=2)).isoformat()
    )
    manager.add_consent(consent1_user1_policyA_v1)
    manager.sign_consent(consent1_user1_policyA_v1)


    consent2_user1_policyA_v2 = UserConsent(
        user_id="user1", policy_id="PolicyA", policy_version="1.1",
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
        timestamp=(datetime.utcnow() - timedelta(days=1)).isoformat(),
        expires_at = (datetime.utcnow() + timedelta(minutes=1)).isoformat() # Expires soon
    )
    manager.add_consent(consent2_user1_policyA_v2)

    consent3_user1_policyB_v1 = UserConsent(
        user_id="user1", policy_id="PolicyB", policy_version="1.0",
        data_categories_consented=[DataCategory.LOCATION_DATA],
        purposes_consented=[Purpose.MARKETING]
    )
    manager.add_consent(consent3_user1_policyB_v1)

    consent4_user2_policyA_v1 = UserConsent(
        user_id="user2", policy_id="PolicyA", policy_version="1.1",
        data_categories_consented=[DataCategory.TECHNICAL_INFO],
        purposes_consented=[Purpose.SECURITY]
    )
    manager.add_consent(consent4_user2_policyA_v1)

    print("--- Initial State ---")
    active_c_u1_pA = manager.get_active_consent("user1", "PolicyA")
    print(f"User1, PolicyA active consent: {active_c_u1_pA.policy_version if active_c_u1_pA else 'None'}")
    assert active_c_u1_pA and active_c_u1_pA.policy_version == "1.1"
    print(f"Is signature valid for consent1? {manager.verify_consent_signature(consent1_user1_policyA_v1)}")


    print("\n--- Testing Expiration ---")
    print(f"User1, PolicyA active consent (v1.1) expires at: {active_c_u1_pA.expires_at if active_c_u1_pA else 'N/A'}")
    import time
    from datetime import timedelta # ensure timedelta is available
    print("Waiting for 65 seconds for consent to expire...")
    # time.sleep(65) # Commented out for faster testing, manually verify logic for expiration

    # Manually expire for test:
    if active_c_u1_pA: # v1.1
         active_c_u1_pA.expires_at = (datetime.utcnow() - timedelta(seconds=1)).isoformat()

    active_c_u1_pA_after_wait = manager.get_active_consent("user1", "PolicyA")
    print(f"User1, PolicyA active consent after waiting: {active_c_u1_pA_after_wait.policy_version if active_c_u1_pA_after_wait else 'None'}")
    # Should fall back to v1.0 (consent1_user1_policyA_v1) if v1.1 (consent2_user1_policyA_v2) expired
    assert active_c_u1_pA_after_wait and active_c_u1_pA_after_wait.policy_version == "1.0"


    print("\n--- Revoking Consent ---")
    print(f"Revoking specific consent: {consent1_user1_policyA_v1.consent_id} (PolicyA v1.0 for user1)")
    manager.revoke_consent(user_id="user1", policy_id="PolicyA", consent_id=consent1_user1_policyA_v1.consent_id)
    active_c_u1_pA_after_revoke = manager.get_active_consent("user1", "PolicyA")
    print(f"User1, PolicyA active consent after specific revoke: {active_c_u1_pA_after_revoke.policy_version if active_c_u1_pA_after_revoke else 'None'}")
    # Now no active consent should be found for user1/PolicyA as v1.1 expired and v1.0 revoked
    assert active_c_u1_pA_after_revoke is None

    # Add a new active consent for user1/PolicyA
    consent5_user1_policyA_v3 = UserConsent(
        user_id="user1", policy_id="PolicyA", policy_version="1.2",
        data_categories_consented=[DataCategory.PERSONAL_INFO],
        purposes_consented=[Purpose.SERVICE_DELIVERY]
    )
    manager.add_consent(consent5_user1_policyA_v3)
    active_c_u1_pA = manager.get_active_consent("user1", "PolicyA")
    print(f"User1, PolicyA active consent now: {active_c_u1_pA.policy_version if active_c_u1_pA else 'None'}")
    assert active_c_u1_pA and active_c_u1_pA.policy_version == "1.2"

    print(f"Revoking latest active consent for user1, PolicyA (which is v1.2)")
    manager.revoke_consent(user_id="user1", policy_id="PolicyA") # Revokes the latest active (v1.2)
    active_c_u1_pA_after_latest_revoke = manager.get_active_consent("user1", "PolicyA")
    print(f"User1, PolicyA active consent after revoking latest: {active_c_u1_pA_after_latest_revoke.policy_version if active_c_u1_pA_after_latest_revoke else 'None'}")
    assert active_c_u1_pA_after_latest_revoke is None


    print("\n--- Consent History ---")
    history_u1_pA = manager.get_consent_history("user1", "PolicyA")
    print(f"User1, PolicyA consent history (count: {len(history_u1_pA)}):")
    for c in history_u1_pA:
        print(f"  ID: {c.consent_id}, Version: {c.policy_version}, Active: {c.is_active}, Timestamp: {c.timestamp}, Expires: {c.expires_at}")
    # Expected: v1.2 (inactive), v1.1 (inactive, expired), v1.0 (inactive, revoked) - order by timestamp desc
    assert len(history_u1_pA) == 3
    assert history_u1_pA[0].policy_version == "1.2" and not history_u1_pA[0].is_active # consent5
    assert history_u1_pA[1].policy_version == "1.1" and not history_u1_pA[1].is_active # consent2
    assert history_u1_pA[2].policy_version == "1.0" and not history_u1_pA[2].is_active # consent1

    print("\n--- Get by ID ---")
    retrieved_by_id = manager.get_consent_by_id(consent3_user1_policyB_v1.consent_id)
    print(f"Retrieved consent by ID ({consent3_user1_policyB_v1.consent_id}): {retrieved_by_id.policy_id if retrieved_by_id else 'Not Found'}")
    assert retrieved_by_id and retrieved_by_id.policy_id == "PolicyB"

    print("\nAll examples executed.")
