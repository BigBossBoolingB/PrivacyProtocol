import unittest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

from privacy_protocol_core.consent_store import ConsentStore
from privacy_protocol_core.consent import UserConsent # Assuming UserConsent is importable
from privacy_protocol_core.policy import DataCategory, Purpose # For example consent data

class TestConsentStore(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.store = ConsentStore(base_path=self.test_dir)

        self.user1 = "userTestOne"
        self.user2_spec_chars = "userTwo/Folder"
        self.policy1 = "PolicyAlpha"
        self.policy2 = "PolicyBeta:123"

        self.ts_now = datetime.now(timezone.utc)
        self.ts_yesterday = self.ts_now - timedelta(days=1)
        self.ts_two_days_ago = self.ts_now - timedelta(days=2)

        self.consent1_u1p1 = UserConsent(
            user_id=self.user1, policy_id=self.policy1, policy_version="1.0",
            timestamp=self.ts_two_days_ago.isoformat(),
            data_categories_consented=[DataCategory.PERSONAL_INFO]
        )
        self.consent2_u1p1_newer = UserConsent(
            user_id=self.user1, policy_id=self.policy1, policy_version="1.1",
            timestamp=self.ts_yesterday.isoformat(),
            data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
            is_active=True
        )
        self.consent3_u1p1_latest_inactive = UserConsent(
            user_id=self.user1, policy_id=self.policy1, policy_version="1.2",
            timestamp=self.ts_now.isoformat(),
            is_active=False # Inactive
        )
        self.consent4_u1p2 = UserConsent(
            user_id=self.user1, policy_id=self.policy2, policy_version="1.0",
            timestamp=self.ts_now.isoformat(),
            data_categories_consented=[DataCategory.LOCATION_DATA]
        )
        self.consent5_u2p1 = UserConsent(
            user_id=self.user2_spec_chars, policy_id=self.policy1, policy_version="1.0",
            timestamp=self.ts_now.isoformat()
        )
        self.consent6_u1p1_expired = UserConsent(
            user_id=self.user1, policy_id=self.policy1, policy_version="1.3",
            timestamp=(self.ts_now - timedelta(minutes=10)).isoformat(), # Newer than consent2
            is_active=True,
            expires_at=(self.ts_now - timedelta(minutes=5)).isoformat() # Expired 5 mins ago
        )


    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_consent(self):
        self.assertTrue(self.store.save_consent(self.consent1_u1p1))
        expected_path = self.store._get_consent_filepath(self.consent1_u1p1)
        self.assertTrue(expected_path.exists())
        with open(expected_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data["consent_id"], self.consent1_u1p1.consent_id)
        self.assertEqual(data["user_id"], self.user1)

    def test_save_consent_with_special_chars_in_ids(self):
        self.assertTrue(self.store.save_consent(self.consent5_u2p1)) # user2_spec_chars
        expected_path_user2 = self.store._get_consent_filepath(self.consent5_u2p1)
        self.assertTrue(expected_path_user2.exists())
        self.assertNotIn("/", expected_path_user2.parent.parent.name) # Check sanitized user_id dir

        self.assertTrue(self.store.save_consent(self.consent4_u1p2)) # policy2 PolicyBeta:123
        expected_path_policy2 = self.store._get_consent_filepath(self.consent4_u1p2)
        self.assertTrue(expected_path_policy2.exists())
        self.assertNotIn(":", expected_path_policy2.parent.name) # Check sanitized policy_id dir

    def test_load_consents_for_user_policy(self):
        self.store.save_consent(self.consent1_u1p1) # ts -2d
        self.store.save_consent(self.consent3_u1p1_latest_inactive) # ts now (inactive)
        self.store.save_consent(self.consent2_u1p1_newer) # ts -1d (active)

        consents = self.store.load_consents_for_user_policy(self.user1, self.policy1)
        self.assertEqual(len(consents), 3)
        # Check sorting (newest first by timestamp)
        self.assertEqual(consents[0].consent_id, self.consent3_u1p1_latest_inactive.consent_id)
        self.assertEqual(consents[1].consent_id, self.consent2_u1p1_newer.consent_id)
        self.assertEqual(consents[2].consent_id, self.consent1_u1p1.consent_id)

    def test_load_latest_active_consent(self):
        self.store.save_consent(self.consent1_u1p1) # Active, but older
        self.store.save_consent(self.consent3_u1p1_latest_inactive) # Newest, but inactive
        self.store.save_consent(self.consent2_u1p1_newer) # Newer and active

        latest_active = self.store.load_latest_active_consent(self.user1, self.policy1)
        self.assertIsNotNone(latest_active)
        self.assertEqual(latest_active.consent_id, self.consent2_u1p1_newer.consent_id)

    def test_load_latest_active_consent_handles_expiration(self):
        self.store.save_consent(self.consent2_u1p1_newer) # Active, timestamp: yesterday
        self.store.save_consent(self.consent6_u1p1_expired) # Active at save, but expired. TS: now-10min, expires: now-5min
                                                       # This makes it newer than consent2

        latest_active = self.store.load_latest_active_consent(self.user1, self.policy1)
        self.assertIsNotNone(latest_active, "Should find an active consent.")
        # consent6 is newer but expired, so it should fall back to consent2
        self.assertEqual(latest_active.consent_id, self.consent2_u1p1_newer.consent_id)

    def test_load_latest_active_consent_none_if_all_inactive_or_expired(self):
        self.consent1_u1p1.is_active = False
        self.store.save_consent(self.consent1_u1p1)
        self.store.save_consent(self.consent6_u1p1_expired) # Already expired

        latest_active = self.store.load_latest_active_consent(self.user1, self.policy1)
        self.assertIsNone(latest_active)

    def test_load_all_consents_for_user(self):
        self.store.save_consent(self.consent1_u1p1) # u1p1
        self.store.save_consent(self.consent2_u1p1_newer) # u1p1
        self.store.save_consent(self.consent4_u1p2) # u1p2
        self.store.save_consent(self.consent5_u2p1) # u2p1 - different user

        user1_consents = self.store.load_all_consents_for_user(self.user1)
        self.assertEqual(len(user1_consents), 3) # c1, c2, c4
        user1_consent_ids = {c.consent_id for c in user1_consents}
        self.assertIn(self.consent1_u1p1.consent_id, user1_consent_ids)
        self.assertIn(self.consent2_u1p1_newer.consent_id, user1_consent_ids)
        self.assertIn(self.consent4_u1p2.consent_id, user1_consent_ids)

        # Check sorting (newest first by timestamp across all policies for the user)
        self.assertEqual(user1_consents[0].consent_id, self.consent4_u1p2.consent_id) # ts_now
        self.assertEqual(user1_consents[1].consent_id, self.consent2_u1p1_newer.consent_id) # ts_yesterday
        self.assertEqual(user1_consents[2].consent_id, self.consent1_u1p1.consent_id) # ts_two_days_ago

    def test_non_existent_user_or_policy_loads_empty(self):
        self.assertEqual(self.store.load_consents_for_user_policy("NoUser", self.policy1), [])
        self.assertIsNone(self.store.load_latest_active_consent(self.user1, "NoPolicy"))
        self.assertEqual(self.store.load_all_consents_for_user("NoUser"), [])

    def test_filename_timestamp_sanitization(self):
        # Example: 2023-10-27T10:30:00.123456+00:00
        # Becomes: 2023-10-27T10-30-00DOT123456ZPLUS00-00
        complex_ts_consent = UserConsent(user_id="ts_user", policy_id="ts_policy",
                                         timestamp="2023-10-27T10:30:00.123456+00:00")
        filepath = self.store._get_consent_filepath(complex_ts_consent)
        filename = filepath.name
        self.assertNotIn(":", filename)
        self.assertNotIn("+", filename) # We replaced + with ZPLUS
        self.assertIn("ZPLUS00-00", filename)
        self.assertIn("DOT123456", filename)
        self.assertTrue(filename.startswith(complex_ts_consent.consent_id))


if __name__ == '__main__':
    unittest.main()
