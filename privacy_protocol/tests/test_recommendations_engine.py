import unittest
import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.recommendations_engine import RecommendationEngine
from privacy_protocol.recommendations_data import REC_ID_OPT_OUT_DATA_SELLING, REC_ID_REVIEW_THIRD_PARTY_POLICIES, REC_ID_MANAGE_COOKIES
from privacy_protocol.privacy_protocol.dashboard_models import UserPrivacyProfile # Import UserPrivacyProfile
from typing import List, Dict # For type hinting if needed in tests

class TestRecommendationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RecommendationEngine()

    def test_validate_rules_valid_data(self):
        # This is implicitly tested by engine initialization if no ValueError is raised.
        # Can add more specific checks if needed, but __init__ calls _validate_rules.
        self.assertIsNotNone(self.engine.recommendation_rules)

    def test_generate_recommendations_for_sentence_data_selling_high_concern(self):
        sentence_analysis = {
            'ai_category': 'Data Selling',
            'user_concern_level': 'High',
            'keyword_matches': [] # Not directly used by current basic triggers
        }
        recommendations = self.engine.generate_recommendations_for_sentence(sentence_analysis)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['id'], REC_ID_OPT_OUT_DATA_SELLING)
        self.assertIn("Opting Out of Data Selling", recommendations[0]['title'])

    def test_generate_recommendations_for_sentence_data_sharing_medium_concern(self):
        sentence_analysis = {
            'ai_category': 'Data Sharing',
            'user_concern_level': 'Medium',
            'keyword_matches': []
        }
        recommendations = self.engine.generate_recommendations_for_sentence(sentence_analysis)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['id'], REC_ID_REVIEW_THIRD_PARTY_POLICIES)

    def test_generate_recommendations_for_sentence_cookies_low_concern(self):
        # Assuming REC_ID_MANAGE_COOKIES triggers on 'Cookies and Tracking Technologies' for Low, Medium, or High
        sentence_analysis = {
            'ai_category': 'Cookies and Tracking Technologies',
            'user_concern_level': 'Low',
            'keyword_matches': []
        }
        recommendations = self.engine.generate_recommendations_for_sentence(sentence_analysis)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['id'], REC_ID_MANAGE_COOKIES)

    def test_generate_recommendations_for_sentence_no_match(self):
        sentence_analysis = {
            'ai_category': 'Contact Information',
            'user_concern_level': 'None',
            'keyword_matches': []
        }
        recommendations = self.engine.generate_recommendations_for_sentence(sentence_analysis)
        self.assertEqual(len(recommendations), 0)

    def test_generate_recommendations_for_sentence_concern_too_low_for_trigger(self):
        # Data Selling rule requires High or Medium concern
        sentence_analysis = {
            'ai_category': 'Data Selling',
            'user_concern_level': 'Low',
            'keyword_matches': []
        }
        recommendations = self.engine.generate_recommendations_for_sentence(sentence_analysis)
        self.assertEqual(len(recommendations), 0)

    def test_augment_analysis_with_recommendations(self):
        analyzed_sentences_data = [
            {
                'ai_category': 'Data Selling',
                'user_concern_level': 'High',
                'keyword_matches': []
            },
            {
                'ai_category': 'Other',
                'user_concern_level': 'None',
                'keyword_matches': []
            }
        ]
        augmented_data = self.engine.augment_analysis_with_recommendations(analyzed_sentences_data)
        self.assertEqual(len(augmented_data), 2)
        self.assertIn('recommendations', augmented_data[0])
        self.assertIn('recommendations', augmented_data[1])
        self.assertEqual(len(augmented_data[0]['recommendations']), 1)
        self.assertEqual(augmented_data[0]['recommendations'][0]['id'], REC_ID_OPT_OUT_DATA_SELLING)
        self.assertEqual(len(augmented_data[1]['recommendations']), 0)

    # --- Tests for generate_global_recommendations ---
    def test_global_recs_no_services(self):
        profile = UserPrivacyProfile(total_services_analyzed=0) # overall_privacy_risk_score will be None
        recommendations = self.engine.generate_global_recommendations(profile)
        # Expect only the generic review recommendation if list is empty by other rules
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]['id'], 'GLOBAL_REGULAR_REVIEW')

    def test_global_recs_high_risk_services_single(self):
        profile = UserPrivacyProfile(
            total_high_risk_services_count=1,
            overall_privacy_risk_score=70,
            total_services_analyzed=1
        )
        recommendations = self.engine.generate_global_recommendations(profile)
        self.assertTrue(any(rec['id'] == 'GLOBAL_HIGH_RISK_ALERT' for rec in recommendations))
        self.assertTrue(any("You have 1 service flagged as high risk" in rec['text'] for rec in recommendations))

    def test_global_recs_high_risk_services_multiple(self):
        profile = UserPrivacyProfile(
            total_high_risk_services_count=3,
            overall_privacy_risk_score=80,
            total_services_analyzed=3
        )
        recommendations = self.engine.generate_global_recommendations(profile)
        self.assertTrue(any(rec['id'] == 'GLOBAL_HIGH_RISK_ALERT' for rec in recommendations))
        self.assertTrue(any("You have 3 service(s) flagged as high risk" in rec['text'] for rec in recommendations))

    def test_global_recs_medium_risk_no_high(self):
        profile = UserPrivacyProfile(
            total_high_risk_services_count=0,
            total_medium_risk_services_count=2,
            overall_privacy_risk_score=50,
            total_services_analyzed=2
        )
        recommendations = self.engine.generate_global_recommendations(profile)
        self.assertTrue(any(rec['id'] == 'GLOBAL_MEDIUM_RISK_INFO' for rec in recommendations))
        self.assertTrue(any("You have 2 service(s) with a 'Medium' privacy risk score" in rec['text'] for rec in recommendations))
        self.assertFalse(any(rec['id'] == 'GLOBAL_HIGH_RISK_ALERT' for rec in recommendations)) # Ensure no high risk alert

    def test_global_recs_all_low_risk_strong_posture(self):
        profile = UserPrivacyProfile(
            total_high_risk_services_count=0,
            total_medium_risk_services_count=0,
            total_low_risk_services_count=2,
            overall_privacy_risk_score=20,
            total_services_analyzed=2
        )
        recommendations = self.engine.generate_global_recommendations(profile)
        # The generic "Regularly Review Settings" is always added if space.
        # The specific "All currently analyzed services have Low privacy risk scores" might not be hit if other generic ones are added first
        # or if the "Your overall privacy posture appears relatively strong" is hit.
        # Based on current logic, "Your overall privacy posture appears relatively strong..." should be present.
        self.assertTrue(any("Your overall privacy posture appears relatively strong" in rec['text'] for rec in recommendations))

    def test_global_recs_moderate_posture_no_specifics(self):
        # Scenario: One medium service, no high. Overall score is medium.
        profile = UserPrivacyProfile(
            total_high_risk_services_count=0,
            total_medium_risk_services_count=1,
            total_low_risk_services_count=0,
            overall_privacy_risk_score=55, # Medium
            total_services_analyzed=1
        )
        recommendations = self.engine.generate_global_recommendations(profile)
        # Expect the specific medium risk insight
        self.assertTrue(any("You have 1 service with a 'Medium' privacy risk score" in rec['text'] for rec in recommendations))
        # And the generic review one
        self.assertTrue(any(rec['id'] == 'GLOBAL_REGULAR_REVIEW' for rec in recommendations))


    def test_global_recs_default_fallback_and_limit(self):
        # Scenario: One high, one medium, one low. Should trigger high risk, then generic.
        profile = UserPrivacyProfile(
            total_high_risk_services_count=1,
            total_medium_risk_services_count=1,
            total_low_risk_services_count=1,
            overall_privacy_risk_score=60, # Example overall
            total_services_analyzed=3
        )
        recommendations = self.engine.generate_global_recommendations(profile)
        self.assertEqual(len(recommendations), 2) # High risk + Generic review
        self.assertEqual(recommendations[0]['id'], 'GLOBAL_HIGH_RISK_ALERT')
        self.assertEqual(recommendations[1]['id'], 'GLOBAL_REGULAR_REVIEW')

        # Scenario: Five high risk services. Max 3 recs.
        # Expects 3 high risk service related recommendations (or 2 specific + 1 summary).
        # The current logic in RecommendationEngine's generate_global_recommendations for multiple high risk:
        # if total_high_risk_services_count > 0 -> appends specific alert.
        # if overall_privacy_risk_score > 66 (and not already high alert or count is 0) -> appends overall high.
        # if total_medium...
        # if len < 3 appends generic.
        # This means it will always prioritize GLOBAL_HIGH_RISK_ALERT first if count > 0.
        # Then, if overall score is also high (which it would be), it would skip GLOBAL_OVERALL_HIGH_RISK if GLOBAL_HIGH_RISK_ALERT was added.
        # Then it would add GLOBAL_REGULAR_REVIEW. So, 2 recommendations.
        profile_many_high = UserPrivacyProfile(
            total_high_risk_services_count=5,
            overall_privacy_risk_score=90,
            total_services_analyzed=5
        )
        recommendations_many_high = self.engine.generate_global_recommendations(profile_many_high)
        self.assertEqual(len(recommendations_many_high), 2)
        self.assertEqual(recommendations_many_high[0]['id'], 'GLOBAL_HIGH_RISK_ALERT')
        self.assertTrue("You have 5 service(s) flagged as high risk" in recommendations_many_high[0]['text'])
        self.assertEqual(recommendations_many_high[1]['id'], 'GLOBAL_REGULAR_REVIEW')


if __name__ == '__main__':
    unittest.main()
