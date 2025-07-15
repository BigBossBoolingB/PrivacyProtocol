import os
import shutil
import unittest
import datetime
from src.privacy_framework.consent_store import ConsentStore
from src.privacy_framework.user_consent import UserConsent

class TestConsentStore(unittest.TestCase):

    def setUp(self):
        self.storage_path = "_test_consents/"
        self.consent_store = ConsentStore(storage_path=self.storage_path)
        self.consent = UserConsent(
            consent_id="test_consent",
            user_id="test_user",
            policy_id="test_policy",
            policy_version=1,
            granted=True,
            timestamp=datetime.datetime.now()
        )

    def tearDown(self):
        if os.path.exists(self.storage_path):
            shutil.rmtree(self.storage_path)

    def test_save_and_load_latest_consent(self):
        self.consent_store.save_consent(self.consent)
        loaded_consent = self.consent_store.load_latest_consent(self.consent.user_id, self.consent.policy_id)
        self.assertEqual(self.consent, loaded_consent)

    def test_load_all_consents(self):
        self.consent_store.save_consent(self.consent)
        all_consents = self.consent_store.load_all_consents(self.consent.user_id)
        self.assertEqual(1, len(all_consents))
        self.assertEqual(self.consent, all_consents[0])

    def test_load_non_existent_consent(self):
        loaded_consent = self.consent_store.load_latest_consent("non_existent_user", "non_existent_policy")
        self.assertIsNone(loaded_consent)

if __name__ == '__main__':
    unittest.main()
