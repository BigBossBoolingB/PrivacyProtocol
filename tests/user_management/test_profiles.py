import unittest
from privacy_protocol_core.user_management.profiles import UserProfile

class TestUserProfile(unittest.TestCase):

    def setUp(self):
        self.user_id = "test_user_123"
        self.profile = UserProfile(self.user_id)

    def test_profile_creation(self):
        self.assertEqual(self.profile.user_id, self.user_id)
        self.assertEqual(self.profile.privacy_tolerance, {})
        self.assertEqual(self.profile.custom_alerts, [])

    def test_set_tolerance(self):
        self.profile.set_tolerance("data_sharing", "low")
        self.assertEqual(self.profile.privacy_tolerance["data_sharing"], "low")

        self.profile.set_tolerance("data_retention", "high")
        self.assertEqual(self.profile.privacy_tolerance["data_retention"], "high")

        # Test updating tolerance
        self.profile.set_tolerance("data_sharing", "medium")
        self.assertEqual(self.profile.privacy_tolerance["data_sharing"], "medium")

    def test_add_custom_alert(self):
        self.profile.add_custom_alert("biometric data")
        self.assertIn("biometric data", self.profile.custom_alerts)

        self.profile.add_custom_alert("children's information")
        self.assertIn("children's information", self.profile.custom_alerts)
        self.assertEqual(len(self.profile.custom_alerts), 2)

if __name__ == '__main__':
    unittest.main()
