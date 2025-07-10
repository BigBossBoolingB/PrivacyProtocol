# tests/test_consent_manager.py
import unittest
import time

# Adjust import path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.consent import UserConsent
from src.privacy_framework.consent_manager import ConsentManager
from src.privacy_framework.policy import DataCategory, Purpose

class TestConsentManager(unittest.TestCase):

    def setUp(self):
        self.manager = ConsentManager()
        self.user_id = "test_user_001"
        self.policy_id_v1 = "policy_xyz_v1"
        self.policy_id_v2 = "policy_xyz_v2" # Different version of same conceptual policy
        self.consent_id_1 = f"consent1_{self.user_id}_{self.policy_id_v1}"

        self.sample_consent1 = UserConsent(
            consent_id=self.consent_id_1,
            user_id=self.user_id,
            policy_id=self.policy_id_v1,
            version=1,
            data_categories_consented=[DataCategory.PERSONAL_INFO],
            purposes_consented=[Purpose.SERVICE_DELIVERY],
            third_parties_consented=[],
            is_active=True,
            timestamp=int(time.time()) - 100 # A bit in the past
        )

    def test_store_and_get_consent_by_id(self):
        self.manager.store_consent(self.sample_consent1)
        retrieved = self.manager.get_consent_by_id(self.consent_id_1)
        self.assertEqual(retrieved, self.sample_consent1)
        self.assertIsNone(self.manager.get_consent_by_id("non_existent_id"))

    def test_get_active_consent_simple(self):
        self.manager.store_consent(self.sample_consent1)
        active = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertEqual(active, self.sample_consent1)

    def test_get_active_consent_no_consent_stored(self):
        active = self.manager.get_active_consent(self.user_id, "unknown_policy")
        self.assertIsNone(active)

    def test_get_active_consent_only_inactive_stored(self):
        self.sample_consent1.is_active = False
        self.manager.store_consent(self.sample_consent1)
        active = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertIsNone(active)

    def test_update_consent_and_active_index(self):
        self.manager.store_consent(self.sample_consent1)
        original_timestamp = self.sample_consent1.timestamp # Store original timestamp

        time.sleep(1.01) # Ensure timestamp changes, wait over a second for int(time.time())
        updated_consent = self.manager.update_consent(
            self.consent_id_1,
            purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
            is_active=True # Ensure it remains active
        )
        self.assertIsNotNone(updated_consent)
        self.assertIn(Purpose.ANALYTICS, updated_consent.purposes_consented)
        self.assertGreater(updated_consent.timestamp, original_timestamp) # Compare with original

        active = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertEqual(active, updated_consent) # Active consent should be the updated one
        self.assertEqual(len(active.purposes_consented), 2)


    def test_deactivate_consent(self):
        self.manager.store_consent(self.sample_consent1) # Initially active

        deactivated = self.manager.deactivate_consent(self.consent_id_1)
        self.assertIsNotNone(deactivated)
        self.assertFalse(deactivated.is_active)

        retrieved_after_deactivation = self.manager.get_consent_by_id(self.consent_id_1)
        self.assertFalse(retrieved_after_deactivation.is_active)

        active_should_be_none = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertIsNone(active_should_be_none)

    def test_active_consent_superseded_by_newer(self):
        self.manager.store_consent(self.sample_consent1) # Older active consent

        time.sleep(0.01) # Ensure timestamp changes
        consent_id_2 = f"consent2_{self.user_id}_{self.policy_id_v1}"
        newer_consent = UserConsent(
            consent_id=consent_id_2, user_id=self.user_id, policy_id=self.policy_id_v1, version=1,
            data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
            purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.MARKETING],
            is_active=True,
            timestamp=int(time.time()) # Newer timestamp
        )
        self.manager.store_consent(newer_consent)

        active = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertEqual(active, newer_consent) # Newer one should be active
        self.assertNotEqual(active, self.sample_consent1)

    def test_storing_older_active_consent_does_not_supersede_newer_active(self):
        time.sleep(0.01)
        consent_id_newer = f"consent_newer_{self.user_id}_{self.policy_id_v1}"
        newer_active_consent = UserConsent(
            consent_id=consent_id_newer, user_id=self.user_id, policy_id=self.policy_id_v1, version=1,
            data_categories_consented=[DataCategory.USAGE_DATA], purposes_consented=[Purpose.ANALYTICS],
            is_active=True, timestamp=int(time.time())
        )
        self.manager.store_consent(newer_active_consent)

        # sample_consent1 has an older timestamp and is also active
        self.manager.store_consent(self.sample_consent1)

        active = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertEqual(active, newer_active_consent) # The newer one should still be active

    def test_sign_consent_placeholder(self):
        self.manager.store_consent(self.sample_consent1)
        signed = self.manager.sign_consent(self.consent_id_1)
        self.assertIsNotNone(signed)
        self.assertTrue(signed.signature.startswith("placeholder_signature_for_"))

        retrieved = self.manager.get_consent_by_id(self.consent_id_1)
        self.assertEqual(retrieved.signature, signed.signature)

    def test_get_all_consents_for_user(self):
        self.manager.store_consent(self.sample_consent1) # timestamp is int(time.time()) - 100

        # Ensure subsequent consents have distinct and later timestamps
        time.sleep(1.01) # Make sure this is later than sample_consent1's base time
        current_ts_for_consent2 = int(time.time())
        consent_id_2 = f"consent2_user1_policyA"
        consent2 = UserConsent(
            consent_id=consent_id_2, user_id=self.user_id, policy_id=self.policy_id_v2, version=2, # Different policy
            data_categories_consented=[DataCategory.LOCATION_DATA], purposes_consented=[Purpose.PERSONALIZATION],
            is_active=True, timestamp=current_ts_for_consent2
        )
        self.manager.store_consent(consent2)

        time.sleep(1.01) # Ensure this is later than consent2
        current_ts_for_consent3 = int(time.time())
        consent_id_3 = f"consent3_user1_policyA_inactive"
        consent3_inactive = UserConsent(
            consent_id=consent_id_3, user_id=self.user_id, policy_id=self.policy_id_v1, version=1,
            data_categories_consented=[DataCategory.PERSONAL_INFO], purposes_consented=[Purpose.SERVICE_DELIVERY],
            is_active=False, timestamp=current_ts_for_consent3 # Newest but inactive
        )
        self.manager.store_consent(consent3_inactive)

        user_consents = self.manager.get_all_consents_for_user(self.user_id)
        self.assertEqual(len(user_consents), 3)
        # Check sorted by timestamp descending
        self.assertEqual(user_consents[0].consent_id, consent_id_3) # consent3_inactive is newest overall
        self.assertEqual(user_consents[1].consent_id, consent_id_2)
        self.assertEqual(user_consents[2].consent_id, self.consent_id_1)

        other_user_consents = self.manager.get_all_consents_for_user("other_user")
        self.assertEqual(len(other_user_consents), 0)

    def test_update_non_existent_consent(self):
        updated = self.manager.update_consent("non_existent", purposes_consented=[Purpose.MARKETING])
        self.assertIsNone(updated)

if __name__ == '__main__':
    unittest.main()
