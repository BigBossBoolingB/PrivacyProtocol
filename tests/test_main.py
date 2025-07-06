import unittest
from privacy_protocol_core.main import PrivacyProtocolApp, main as main_script_entry
from privacy_protocol_core.user_management.profiles import UserProfile
# It might be useful to mock stdout for tests that print a lot
from io import StringIO
import sys

class TestPrivacyProtocolApp(unittest.TestCase):

    def setUp(self):
        self.app = PrivacyProtocolApp()
        self.user_id = "test_main_user"
        self.policy_url = "http://example-privacy.com/policy"
        self.policy_text_simple = "This is a simple policy."
        self.policy_text_complex = "This policy mentions data selling and third-party sharing for profit."

    def test_app_initialization(self):
        self.assertIsNotNone(self.app.interpreter)
        self.assertIsNotNone(self.app.clause_identifier)
        self.assertIsNotNone(self.app.risk_scorer)
        # ... and so on for all components

    def test_get_or_create_user_profile(self):
        profile = self.app.get_or_create_user_profile(self.user_id)
        self.assertIsInstance(profile, UserProfile)
        self.assertEqual(profile.user_id, self.user_id)

        # Test that it returns the same profile if called again
        profile_again = self.app.get_or_create_user_profile(self.user_id)
        self.assertIs(profile, profile_again) # Check for object identity

    def test_analyze_policy_basic_structure(self):
        analysis = self.app.analyze_policy(self.user_id, self.policy_url, self.policy_text_simple)

        self.assertIn("plain_language_summary", analysis)
        self.assertIn("disagreeable_clauses", analysis)
        self.assertIn("questionable_clauses", analysis)
        self.assertIn("risk_score", analysis)
        self.assertIn("recommendations", analysis)

        self.assertIsInstance(analysis["risk_score"], (int, float))

    def test_analyze_policy_risk_score_variation(self):
        # User with low tolerance for data sharing
        profile = self.app.get_or_create_user_profile(self.user_id)
        profile.set_tolerance("data_sharing", "low")

        analysis_complex_low_tolerance = self.app.analyze_policy(self.user_id, self.policy_url, self.policy_text_complex)

        # Create a new user profile with high tolerance for comparison
        user_id_high_tolerance = "user_high_tolerance"
        profile_high = self.app.get_or_create_user_profile(user_id_high_tolerance)
        # Default or explicit high tolerance
        # profile_high.set_tolerance("data_sharing", "high") # Assuming default is not "low"

        analysis_complex_high_tolerance = self.app.analyze_policy(user_id_high_tolerance, self.policy_url, self.policy_text_complex)

        # Based on current placeholder logic in scorer:
        # policy_text_complex contains "data selling" (score +50)
        # low tolerance for data_sharing adds +20
        self.assertEqual(analysis_complex_low_tolerance["risk_score"], 70)
        self.assertEqual(analysis_complex_high_tolerance["risk_score"], 50)


    def test_main_script_entry_runs(self):
        # Test if the main() function in main.py runs without crashing
        # This is a very basic check. We can capture stdout to check output if needed.
        saved_stdout = sys.stdout
        try
            out = StringIO()
            sys.stdout = out
            main_script_entry() # Call the main function from __main__
            output = out.getvalue().strip()
            self.assertIn("PrivacyProtocolApp initialized.", output)
            self.assertIn("--- Analysis Result ---", output)
        finally:
            sys.stdout = saved_stdout

    # TODO: Add more tests for interaction between components, edge cases, etc.

if __name__ == '__main__':
    unittest.main()
