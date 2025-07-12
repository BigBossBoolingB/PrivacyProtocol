# tests/test_consent_manager.py
import unittest
import time
import shutil # <--- Added import

# Adjust import path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.consent import UserConsent
from src.privacy_framework.consent_manager import ConsentManager
from src.privacy_framework.policy import DataCategory, Purpose

from src.privacy_framework.consent_store import ConsentStore # Import the store

class TestConsentManager(unittest.TestCase):
    TEST_CM_STORAGE_PATH = "_app_data_test/consent_manager_specific_consents/"

    def setUp(self):
        # Ensure a clean state for each test
        if os.path.exists(self.TEST_CM_STORAGE_PATH):
            shutil.rmtree(self.TEST_CM_STORAGE_PATH)

        self.consent_store_for_manager = ConsentStore(storage_path=self.TEST_CM_STORAGE_PATH)
        self.manager = ConsentManager(consent_store=self.consent_store_for_manager)


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

    def tearDown(self):
        """Clean up the storage directory after each test."""
        if os.path.exists(self.TEST_CM_STORAGE_PATH):
            shutil.rmtree(self.TEST_CM_STORAGE_PATH)

    def test_store_and_get_consent_by_id(self):
        self.manager.grant_consent(self.sample_consent1) # Changed from store_consent
        retrieved = self.manager.get_consent_by_id(self.user_id, self.consent_id_1) # Added user_id
        self.assertEqual(retrieved, self.sample_consent1)
        self.assertIsNone(self.manager.get_consent_by_id(self.user_id, "non_existent_id")) # Added user_id

    def test_get_active_consent_simple(self):
        self.manager.grant_consent(self.sample_consent1) # Changed from store_consent
        active = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertEqual(active, self.sample_consent1)

    def test_get_active_consent_no_consent_stored(self):
        active = self.manager.get_active_consent(self.user_id, "unknown_policy")
        self.assertIsNone(active)

    def test_get_active_consent_only_inactive_stored(self):
        self.sample_consent1.is_active = False
        self.manager.grant_consent(self.sample_consent1) # Changed from store_consent
        active = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertIsNone(active)

    def test_update_consent_and_active_index(self): # Renamed to update_consent_details
        self.manager.grant_consent(self.sample_consent1) # Changed from store_consent
        original_timestamp = self.sample_consent1.timestamp # Store original timestamp

        time.sleep(1.01) # Ensure timestamp changes, wait over a second for int(time.time())
        updated_consent = self.manager.update_consent_details( # Renamed and added user_id
            user_id=self.user_id,
            consent_id=self.consent_id_1,
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
        self.manager.grant_consent(self.sample_consent1) # Initially active

        deactivated = self.manager.deactivate_consent(user_id=self.user_id, consent_id=self.consent_id_1) # Added user_id
        self.assertIsNotNone(deactivated)
        self.assertFalse(deactivated.is_active)

        retrieved_after_deactivation = self.manager.get_consent_by_id(self.user_id, self.consent_id_1) # Added user_id
        self.assertFalse(retrieved_after_deactivation.is_active)

        active_should_be_none = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertIsNone(active_should_be_none)

    def test_active_consent_superseded_by_newer(self):
        self.manager.grant_consent(self.sample_consent1) # Older active consent; changed from store_consent

        time.sleep(0.01) # Ensure timestamp changes
        consent_id_2 = f"consent2_{self.user_id}_{self.policy_id_v1}"
        newer_consent = UserConsent(
            consent_id=consent_id_2, user_id=self.user_id, policy_id=self.policy_id_v1, version=1,
            data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
            purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.MARKETING],
            third_parties_consented=[], # Added default
            is_active=True,
            timestamp=int(time.time()) # Newer timestamp
        )
        self.manager.grant_consent(newer_consent) # Changed from store_consent

        active = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertEqual(active, newer_consent) # Newer one should be active
        self.assertNotEqual(active, self.sample_consent1)

    def test_storing_older_active_consent_does_not_supersede_newer_active(self):
        time.sleep(0.01)
        consent_id_newer = f"consent_newer_{self.user_id}_{self.policy_id_v1}"
        newer_active_consent = UserConsent(
            consent_id=consent_id_newer, user_id=self.user_id, policy_id=self.policy_id_v1, version=1,
            data_categories_consented=[DataCategory.USAGE_DATA], purposes_consented=[Purpose.ANALYTICS],
            third_parties_consented=[], # Added default
            is_active=True, timestamp=int(time.time())
        )
        self.manager.grant_consent(newer_active_consent) # Changed from store_consent

        # sample_consent1 has an older timestamp and is also active
        self.manager.grant_consent(self.sample_consent1) # Changed from store_consent

        active = self.manager.get_active_consent(self.user_id, self.policy_id_v1)
        self.assertEqual(active, newer_active_consent) # The newer one should still be active

    def test_sign_consent_placeholder(self):
        self.manager.grant_consent(self.sample_consent1) # Changed from store_consent
        signed = self.manager.sign_consent(user_id=self.user_id, consent_id=self.sample_consent1.consent_id) # Corrected consent_id
        self.assertIsNotNone(signed)
        self.assertEqual(signed.signature, "hash_sig_debug_placeholder") # Expect exact debug signature

        retrieved = self.manager.get_consent_by_id(self.user_id, self.sample_consent1.consent_id) # Corrected consent_id
        self.assertEqual(retrieved.signature, signed.signature)

    def test_get_all_consents_for_user(self):
        self.manager.grant_consent(self.sample_consent1) # timestamp is int(time.time()) - 100; changed from store_consent

        # Ensure subsequent consents have distinct and later timestamps
        time.sleep(1.01) # Make sure this is later than sample_consent1's base time
        current_ts_for_consent2 = int(time.time())
        consent_id_2 = f"consent2_user1_policyA"
        consent2 = UserConsent(
            consent_id=consent_id_2, user_id=self.user_id, policy_id=self.policy_id_v2, version=2, # Different policy
            data_categories_consented=[DataCategory.LOCATION_DATA], purposes_consented=[Purpose.PERSONALIZATION],
            third_parties_consented=[], # Added default
            is_active=True, timestamp=current_ts_for_consent2
        )
        self.manager.grant_consent(consent2) # Changed from store_consent

        time.sleep(1.01) # Ensure this is later than consent2
        current_ts_for_consent3 = int(time.time())
        consent_id_3 = f"consent3_user1_policyA_inactive"
        consent3_inactive = UserConsent(
            consent_id=consent_id_3, user_id=self.user_id, policy_id=self.policy_id_v1, version=1,
            data_categories_consented=[DataCategory.PERSONAL_INFO], purposes_consented=[Purpose.SERVICE_DELIVERY],
            third_parties_consented=[], # Added default
            is_active=False, timestamp=current_ts_for_consent3 # Newest but inactive
        )
        self.manager.grant_consent(consent3_inactive) # Changed from store_consent

        user_consents = self.manager.get_all_consents_for_user(self.user_id)
        self.assertEqual(len(user_consents), 3)
        # Check sorted by timestamp descending
        self.assertEqual(user_consents[0].consent_id, consent_id_3) # consent3_inactive is newest overall
        self.assertEqual(user_consents[1].consent_id, consent_id_2)
        self.assertEqual(user_consents[2].consent_id, self.consent_id_1)

        other_user_consents = self.manager.get_all_consents_for_user("other_user")
        self.assertEqual(len(other_user_consents), 0)

    def test_update_non_existent_consent(self):
        updated = self.manager.update_consent_details( # Renamed and added user_id
            user_id=self.user_id,
            consent_id="non_existent",
            purposes_consented=[Purpose.MARKETING]
        )
        self.assertIsNone(updated)

    def test_verify_consent_signature_placeholder(self):
        self.manager.grant_consent(self.sample_consent1)

        # Sign it first
        signed_consent = self.manager.sign_consent(user_id=self.user_id, consent_id=self.sample_consent1.consent_id)
        self.assertIsNotNone(signed_consent)
        self.assertIsNotNone(signed_consent.signature)

        # Verify (conceptually)
        is_valid = self.manager.verify_consent_signature(user_id=self.user_id, consent_id=self.sample_consent1.consent_id)
        # Current placeholder verify_consent_signature is very basic and might just check for presence or a specific format.
        # If it's comparing hashes based on current state, it might be tricky due to timestamp updates.
        # For this test, we'll assume the placeholder logic will pass if a signature that it generated is present.
        self.assertTrue(is_valid, "Conceptual signature verification should pass for a signed consent.")

        # Test with a consent that has no signature
        consent_no_sig_id = "no_sig_consent"
        consent_no_sig = UserConsent(
            consent_id=consent_no_sig_id, user_id=self.user_id, policy_id=self.policy_id_v1, version=1,
            data_categories_consented=[], purposes_consented=[], timestamp=int(time.time())
        )
        self.manager.grant_consent(consent_no_sig)
        is_valid_no_sig = self.manager.verify_consent_signature(user_id=self.user_id, consent_id=consent_no_sig_id)
        self.assertFalse(is_valid_no_sig, "Verification should fail if no signature is present.")

        # Test with a consent that has a manually tampered/incorrect signature
        tampered_consent_id = "tampered_sig_consent"
        tampered_consent = UserConsent(
            consent_id=tampered_consent_id, user_id=self.user_id, policy_id=self.policy_id_v1, version=1,
            data_categories_consented=[], purposes_consented=[], timestamp=int(time.time()),
            signature="clearly_not_a_valid_placeholder_hash_sig"
        )
        self.manager.grant_consent(tampered_consent)
        is_valid_tampered = self.manager.verify_consent_signature(user_id=self.user_id, consent_id=tampered_consent_id)
        self.assertFalse(is_valid_tampered, "Verification should fail for a signature with an unknown format.")


if __name__ == '__main__':
    unittest.main()
