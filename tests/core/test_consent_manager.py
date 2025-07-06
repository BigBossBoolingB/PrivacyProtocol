import unittest
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from privacy_protocol_core.consent_manager import ConsentManager
from privacy_protocol_core.consent import UserConsent
from privacy_protocol_core.policy import DataCategory, Purpose # For example consents
from privacy_protocol_core.consent_store import ConsentStore

class TestConsentManagerWithStore(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.consent_store = ConsentStore(base_path=self.test_dir)
        self.manager = ConsentManager(consent_store=self.consent_store)

        self.user_id1 = "user_store_1"
        self.policy_id1 = "policy_store_A"
        self.policy_id2 = "policy_store_B"

        # Timestamps
        self.ts_now = datetime.now(timezone.utc)
        self.ts_minus_1_hr = self.ts_now - timedelta(hours=1)
        self.ts_minus_2_hr = self.ts_now - timedelta(hours=2)
        self.ts_plus_1_hr = self.ts_now + timedelta(hours=1)


        self.consent1 = UserConsent(
            user_id=self.user_id1, policy_id=self.policy_id1, policy_version="1.0",
            timestamp=self.ts_minus_2_hr.isoformat() # Oldest
        )
        self.consent2_active = UserConsent(
            user_id=self.user_id1, policy_id=self.policy_id1, policy_version="1.1",
            timestamp=self.ts_minus_1_hr.isoformat(), # Newer
            is_active=True
        )
        self.consent3_latest_but_inactive = UserConsent(
            user_id=self.user_id1, policy_id=self.policy_id1, policy_version="1.2",
            timestamp=self.ts_now.isoformat(), # Newest
            is_active=False
        )
        self.consent4_other_policy = UserConsent(
            user_id=self.user_id1, policy_id=self.policy_id2, policy_version="1.0",
            timestamp=self.ts_now.isoformat()
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_add_consent_persists(self):
        self.manager.add_consent(self.consent1)
        # Re-initialize manager with the same store to simulate app restart / different instance
        new_manager = ConsentManager(self.consent_store)
        retrieved = new_manager.get_consent_by_id(self.user_id1, self.policy_id1, self.consent1.consent_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.consent_id, self.consent1.consent_id)
        self.assertEqual(retrieved.policy_version, "1.0")

    def test_add_consent_deactivates_older_active_in_store(self):
        self.manager.add_consent(self.consent1) # consent1 is active by default, ts = -2hr
        self.assertTrue(self.consent1.is_active)

        # Add a newer active consent
        self.manager.add_consent(self.consent2_active) # ts = -1hr
        self.assertTrue(self.consent2_active.is_active)

        # Check consent1 status from store via a new manager instance
        new_manager = ConsentManager(self.consent_store)
        consent1_from_store = new_manager.get_consent_by_id(self.user_id1, self.policy_id1, self.consent1.consent_id)
        self.assertIsNotNone(consent1_from_store)
        self.assertFalse(consent1_from_store.is_active, "Older consent (consent1) should have been deactivated in store.")

        active_consent = new_manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertEqual(active_consent.consent_id, self.consent2_active.consent_id)

    def test_get_active_consent_from_store(self):
        self.manager.add_consent(self.consent1) # Active, ts -2hr
        self.manager.add_consent(self.consent3_latest_but_inactive) # Inactive, ts now
        self.manager.add_consent(self.consent2_active) # Active, ts -1hr (should be this one)

        active = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNotNone(active)
        self.assertEqual(active.consent_id, self.consent2_active.consent_id)

    def test_get_active_consent_handles_expiration_from_store(self):
        expiring_consent = UserConsent(
            user_id=self.user_id1, policy_id=self.policy_id1, policy_version="2.0",
            timestamp=self.ts_now.isoformat(), # Newest timestamp
            is_active=True,
            expires_at=(self.ts_now + timedelta(seconds=1)).isoformat() # Expires very soon
        )
        still_valid_consent = UserConsent( # Older but non-expiring
            user_id=self.user_id1, policy_id=self.policy_id1, policy_version="0.9",
            timestamp=self.ts_minus_2_hr.isoformat(), is_active=True
        )
        self.manager.add_consent(still_valid_consent)
        self.manager.add_consent(expiring_consent)

        active = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertEqual(active.consent_id, expiring_consent.consent_id, "Expiring consent should be active initially.")

        # Simulate time passing for expiration (by directly modifying and re-saving to store)
        expiring_consent.expires_at = (self.ts_now - timedelta(seconds=1)).isoformat() # Now expired
        self.consent_store.save_consent(expiring_consent) # Update in store

        active_after_expiry = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        # After expiring_consent (which was the latest active) expires,
        # and still_valid_consent was previously deactivated by adding expiring_consent,
        # there should be no active consent left.
        self.assertIsNone(active_after_expiry, "Should be None as the latest active consent expired and older ones were already inactive.")


    def test_revoke_consent_by_id_persists(self):
        self.manager.add_consent(self.consent2_active) # Initially active
        self.assertTrue(self.consent2_active.is_active)

        self.manager.revoke_consent(self.user_id1, self.policy_id1, self.consent2_active.consent_id)

        # Verify through a new manager/store instance
        new_manager = ConsentManager(self.consent_store)
        revoked_from_store = new_manager.get_consent_by_id(self.user_id1, self.policy_id1, self.consent2_active.consent_id)
        self.assertIsNotNone(revoked_from_store)
        self.assertFalse(revoked_from_store.is_active)

        active_consent = new_manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNone(active_consent, "No active consent should remain.")


    def test_revoke_active_consent_without_id_persists(self):
        self.manager.add_consent(self.consent1) # Will be made inactive by consent2
        self.manager.add_consent(self.consent2_active) # This is the one to be revoked

        self.manager.revoke_consent(self.user_id1, self.policy_id1) # No ID, targets active (consent2_active)

        new_manager = ConsentManager(self.consent_store)
        consent2_from_store = new_manager.get_consent_by_id(self.user_id1, self.policy_id1, self.consent2_active.consent_id)
        self.assertIsNotNone(consent2_from_store)
        self.assertFalse(consent2_from_store.is_active, "Targeted active consent should be inactive in store.")

        active_consent = new_manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNone(active_consent)


    def test_get_consent_history_from_store(self):
        self.manager.add_consent(self.consent1)
        self.manager.add_consent(self.consent2_active)
        self.manager.add_consent(self.consent3_latest_but_inactive)

        new_manager = ConsentManager(self.consent_store)
        history = new_manager.get_consent_history(self.user_id1, self.policy_id1)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].consent_id, self.consent3_latest_but_inactive.consent_id)
        self.assertEqual(history[1].consent_id, self.consent2_active.consent_id)
        self.assertEqual(history[2].consent_id, self.consent1.consent_id)

    def test_get_consent_by_id_from_store(self):
        self.manager.add_consent(self.consent1)
        self.manager.add_consent(self.consent4_other_policy)

        new_manager = ConsentManager(self.consent_store)
        retrieved1 = new_manager.get_consent_by_id(self.user_id1, self.policy_id1, self.consent1.consent_id)
        self.assertEqual(retrieved1.consent_id, self.consent1.consent_id)

        retrieved_other = new_manager.get_consent_by_id(self.user_id1, self.policy_id2, self.consent4_other_policy.consent_id)
        self.assertEqual(retrieved_other.consent_id, self.consent4_other_policy.consent_id)

        non_existent = new_manager.get_consent_by_id(self.user_id1, self.policy_id1, "non-existent-id")
        self.assertIsNone(non_existent)

    def test_sign_and_verify_placeholders(self):
        # These methods are simple placeholders, just test they run.
        # Interaction with store for signatures is not part of this test.
        signed_consent = self.manager.sign_consent(self.consent1)
        self.assertTrue(signed_consent.signature.startswith("signed_placeholder_"))
        self.assertTrue(self.manager.verify_consent_signature(signed_consent))

        signed_consent.signature = "invalid"
        self.assertFalse(self.manager.verify_consent_signature(signed_consent))

if __name__ == '__main__':
    unittest.main()
