import unittest
from privacy_protocol_core.action_center.recommender import Recommender
from privacy_protocol_core.user_management.profiles import UserProfile

class TestRecommender(unittest.TestCase):

    def setUp(self):
        self.recommender = Recommender()
        self.test_user_profile = UserProfile("reco_user")

    def test_generate_recommendations_high_risk(self):
        policy_text = "This policy is very risky."
        risk_score = 80 # High risk
        recommendations = self.recommender.generate_recommendations(policy_text, risk_score)
        self.assertIn("High risk policy detected. Consider opting out of non-essential services.", recommendations)

    def test_generate_recommendations_third_party_sharing(self):
        policy_text = "We share your data with third-party sharing partners."
        risk_score = 60 # Medium risk
        recommendations = self.recommender.generate_recommendations(policy_text, risk_score)
        self.assertIn("This policy mentions sharing data with third parties. Review these clauses carefully.", recommendations)

    def test_generate_recommendations_low_risk(self):
        policy_text = "This policy is fine."
        risk_score = 30 # Low risk
        recommendations = self.recommender.generate_recommendations(policy_text, risk_score)
        # Expect no specific recommendations based on current simple logic for low risk
        self.assertEqual(len(recommendations), 0)

    def test_generate_recommendations_with_user_profile(self):
        # This test is a placeholder as current recommender doesn't use user_profile extensively
        policy_text = "Some policy text."
        risk_score = 50
        self.test_user_profile.set_tolerance("data_sharing", "low")
        recommendations = self.recommender.generate_recommendations(policy_text, risk_score, self.test_user_profile)
        # Basic check, more specific tests needed when logic is implemented
        self.assertIsInstance(recommendations, list)

    def test_suggest_alternatives_email(self):
        alternatives = self.recommender.suggest_alternatives("email_provider")
        self.assertIn("ProtonMail", alternatives)
        self.assertIn("Tutanota", alternatives)

    def test_suggest_alternatives_unknown(self):
        alternatives = self.recommender.suggest_alternatives("unknown_service_type")
        self.assertEqual(alternatives, [])

    # TODO: Add more tests as recommendation logic becomes more sophisticated.

if __name__ == '__main__':
    unittest.main()
