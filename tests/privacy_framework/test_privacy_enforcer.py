import unittest
from unittest.mock import MagicMock
from src.privacy_framework.privacy_enforcer import PrivacyEnforcer
from src.privacy_framework.privacy_policy import PrivacyPolicy
from src.privacy_framework.user_consent import UserConsent
import datetime

class TestPrivacyEnforcer(unittest.TestCase):

    def setUp(self):
        self.policy_store = MagicMock()
        self.consent_manager = MagicMock()
        self.auditor = MagicMock()
        self.enforcer = PrivacyEnforcer(self.policy_store, self.consent_manager, self.auditor)

        self.policy = PrivacyPolicy("test_policy", 1, "content", ["allow_analytics"])
        self.consent = UserConsent("c1", "u1", "p1", 1, True, datetime.datetime.now())

    def test_process_data_stream_analytics_allowed(self):
        self.policy_store.load_policy.return_value = self.policy
        self.consent_manager.consent_store.load_latest_consent.return_value = self.consent

        data = {"email": "test@test.com"}
        result = self.enforcer.process_data_stream("u1", "p1", data, "Analytics")

        self.assertEqual(result['privacy_status'], "Permitted_Obfuscated")
        self.assertEqual(result['email'], "********")
        self.auditor.log_event.assert_called_once()

    def test_process_data_stream_marketing_denied(self):
        self.policy_store.load_policy.return_value = self.policy
        self.consent_manager.consent_store.load_latest_consent.return_value = self.consent

        data = {"email": "test@test.com"}
        result = self.enforcer.process_data_stream("u1", "p1", data, "Marketing")

        self.assertEqual(result['privacy_status'], "Denied")
        self.assertEqual(result['email'], "test@test.com")
        self.auditor.log_event.assert_not_called()

if __name__ == '__main__':
    unittest.main()
