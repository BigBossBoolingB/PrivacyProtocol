import unittest
from datetime import datetime, timedelta, timezone
from privacy_protocol_core.consent_manager import ConsentManager
from privacy_protocol_core.consent import UserConsent
from privacy_protocol_core.policy import DataCategory, Purpose # For example consents

class TestConsentManager(unittest.TestCase):

    def setUp(self):
        self.manager = ConsentManager()
        self.user_id1 = "test_user_1"
        self.user_id2 = "test_user_2"
        self.policy_id1 = "test_policy_A"
        self.policy_id2 = "test_policy_B"

        self.consent1 = UserConsent(
            user_id=self.user_id1, policy_id=self.policy_id1, policy_version="1.0",
            data_categories_consented=[DataCategory.PERSONAL_INFO],
            purposes_consented=[Purpose.SERVICE_DELIVERY],
            timestamp=(datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        )
        self.consent2_v1_1 = UserConsent(
            user_id=self.user_id1, policy_id=self.policy_id1, policy_version="1.1",
            data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
            purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
            timestamp=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        )
        self.consent3_policyB = UserConsent(
            user_id=self.user_id1, policy_id=self.policy_id2, policy_version="1.0",
            data_categories_consented=[DataCategory.LOCATION_DATA],
            purposes_consented=[Purpose.MARKETING]
        )
        self.consent4_user2_policyA = UserConsent(
            user_id=self.user_id2, policy_id=self.policy_id1, policy_version="1.1",
            data_categories_consented=[DataCategory.TECHNICAL_INFO],
            purposes_consented=[Purpose.SECURITY]
        )

    def test_add_consent_and_get_by_id(self):
        self.manager.add_consent(self.consent1)
        retrieved = self.manager.get_consent_by_id(self.consent1.consent_id)
        self.assertEqual(retrieved, self.consent1)
        self.assertEqual(retrieved.user_id, self.user_id1)

    def test_add_consent_updates_existing_with_same_id(self):
        self.manager.add_consent(self.consent1)
        updated_consent1 = UserConsent(
            consent_id=self.consent1.consent_id, # Same ID
            user_id=self.user_id1, policy_id=self.policy_id1, policy_version="1.0.1",
            data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.FINANCIAL_INFO], # Changed
            purposes_consented=[Purpose.SERVICE_DELIVERY],
            timestamp=self.consent1.timestamp
        )
        self.manager.add_consent(updated_consent1)
        retrieved = self.manager.get_consent_by_id(self.consent1.consent_id)
        self.assertEqual(retrieved.policy_version, "1.0.1")
        self.assertIn(DataCategory.FINANCIAL_INFO, retrieved.data_categories_consented)

        history = self.manager.get_consent_history(self.user_id1, self.policy_id1)
        self.assertEqual(len(history), 1) # Should update in place, not add new due to same ID


    def test_get_active_consent(self):
        self.manager.add_consent(self.consent1) # Older, v1.0
        self.manager.add_consent(self.consent2_v1_1) # Newer, v1.1, should be active

        active_consent = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNotNone(active_consent)
        self.assertEqual(active_consent.consent_id, self.consent2_v1_1.consent_id)
        self.assertEqual(active_consent.policy_version, "1.1")

    def test_get_active_consent_deactivates_older_on_add(self):
        # Add newer consent first, then older. Older should not deactivate newer.
        self.manager.add_consent(self.consent2_v1_1)
        self.manager.add_consent(self.consent1)

        active_consent = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertEqual(active_consent.consent_id, self.consent2_v1_1.consent_id, "Newer consent should remain active")

        # Reset and add older first, then newer. Newer should deactivate older.
        self.manager = ConsentManager()
        self.manager.add_consent(self.consent1)
        self.assertTrue(self.consent1.is_active)
        self.manager.add_consent(self.consent2_v1_1) # This is newer and active

        self.assertFalse(self.consent1.is_active, "Older consent (consent1) should be deactivated by newer (consent2_v1_1)")
        self.assertTrue(self.consent2_v1_1.is_active)
        active_consent_after = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertEqual(active_consent_after.consent_id, self.consent2_v1_1.consent_id)


    def test_get_active_consent_none_if_no_active(self):
        self.consent1.is_active = False
        self.manager.add_consent(self.consent1)
        active_consent = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNone(active_consent)

    def test_get_active_consent_handles_expiration(self):
        expired_consent = UserConsent(
            user_id=self.user_id1, policy_id=self.policy_id1, policy_version="0.9",
            timestamp=(datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
            expires_at=(datetime.now(timezone.utc) - timedelta(hours=1)).isoformat() # Expired 1 hour ago
        )
        self.manager.add_consent(expired_consent)
        self.manager.add_consent(self.consent1) # Active, older than expired_consent but not expired

        active = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNotNone(active)
        self.assertEqual(active.consent_id, self.consent1.consent_id, "Should return non-expired consent1")
        self.assertFalse(expired_consent.is_active, "Expired consent should be marked inactive by get_active_consent")

        # Test case where only an expired consent exists
        self.manager = ConsentManager()
        expired_consent.is_active = True # Reset for this test
        self.manager.add_consent(expired_consent)
        active_should_be_none = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNone(active_should_be_none, "Should return None if only expired consent exists")


    def test_revoke_consent_by_id(self):
        self.manager.add_consent(self.consent1) # Active initially
        self.manager.add_consent(self.consent2_v1_1) # Now this is active, consent1 becomes inactive

        # Target: Revoke consent2_v1_1 (which is currently active) by its ID
        self.assertTrue(self.consent2_v1_1.is_active)
        revoked = self.manager.revoke_consent(user_id=self.user_id1, policy_id=self.policy_id1, consent_id=self.consent2_v1_1.consent_id)
        self.assertTrue(revoked, "Revocation by ID should succeed for an active consent.")
        self.assertFalse(self.consent2_v1_1.is_active, "Consent2_v1_1 should be inactive after revocation by ID.")

        # consent1 should remain inactive as it was before this specific revocation
        self.assertFalse(self.consent1.is_active, "Consent1 should remain inactive.")

        # No active consent should be found for user1/PolicyA now
        active_consent = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNone(active_consent, "No active consent should exist after revoking the only active one by ID.")

    def test_revoke_inactive_consent_by_id(self):
        self.manager.add_consent(self.consent1) # Active initially
        self.manager.add_consent(self.consent2_v1_1) # Now this is active, consent1 becomes inactive

        # Target: Revoke consent1 (which is currently inactive) by its ID
        self.assertFalse(self.consent1.is_active, "Consent1 should be inactive before targeted revocation.")
        revoked = self.manager.revoke_consent(user_id=self.user_id1, policy_id=self.policy_id1, consent_id=self.consent1.consent_id)
        self.assertTrue(revoked, "Revocation by ID should still 'succeed' for an already inactive consent (marks it as explicitly revoked).")
        self.assertFalse(self.consent1.is_active, "Consent1 should remain inactive.")

        # consent2_v1_1 should remain active
        active_consent = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNotNone(active_consent)
        self.assertEqual(active_consent.consent_id, self.consent2_v1_1.consent_id, "Consent2_v1_1 should still be active.")
        self.assertTrue(active_consent.is_active)


    def test_revoke_active_consent_without_id(self):
        self.manager.add_consent(self.consent1) # older, becomes inactive
        self.manager.add_consent(self.consent2_v1_1) # newer, active

        self.assertTrue(self.consent2_v1_1.is_active)
        revoked = self.manager.revoke_consent(user_id=self.user_id1, policy_id=self.policy_id1) # No ID, targets active
        self.assertTrue(revoked)

        self.assertFalse(self.consent2_v1_1.is_active, "The previously active consent (consent2_v1_1) should now be inactive.")

        active_consent = self.manager.get_active_consent(self.user_id1, self.policy_id1)
        self.assertIsNone(active_consent, "No active consent should remain for user1/policy1 after general revocation.")


    def test_get_consent_history(self):
        # Timestamps are crucial for order. consent2 is newer than consent1.
        # consent1: now - 2 days
        # consent2_v1_1: now - 1 day
        self.manager.add_consent(self.consent1)
        self.manager.add_consent(self.consent2_v1_1) # ts = now - 1 day (newest)
        self.manager.add_consent(self.consent3_policyB) # Different policy

        history = self.manager.get_consent_history(self.user_id1, self.policy_id1)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].consent_id, self.consent2_v1_1.consent_id, "History should be newest first")
        self.assertEqual(history[1].consent_id, self.consent1.consent_id)

        history_policy_b = self.manager.get_consent_history(self.user_id1, self.policy_id2)
        self.assertEqual(len(history_policy_b), 1)
        self.assertEqual(history_policy_b[0].consent_id, self.consent3_policyB.consent_id)

        empty_history = self.manager.get_consent_history("non_existent_user", self.policy_id1)
        self.assertEqual(len(empty_history), 0)

    def test_add_consent_value_errors(self):
        with self.assertRaisesRegex(ValueError, "Invalid consent object provided"):
            self.manager.add_consent("not a consent object")

        invalid_consent_no_ids = UserConsent()
        with self.assertRaisesRegex(ValueError, "User ID and Policy ID must be set"):
            self.manager.add_consent(invalid_consent_no_ids)

    def test_sign_and_verify_consent_placeholders(self):
        self.manager.sign_consent(self.consent1)
        self.assertIsNotNone(self.consent1.signature)
        self.assertTrue(self.consent1.signature.startswith("signed_placeholder_"))

        is_valid = self.manager.verify_consent_signature(self.consent1)
        self.assertTrue(is_valid)

        self.consent1.signature = "tampered_sig"
        is_valid_tampered = self.manager.verify_consent_signature(self.consent1)
        self.assertFalse(is_valid_tampered)

if __name__ == '__main__':
    unittest.main()
