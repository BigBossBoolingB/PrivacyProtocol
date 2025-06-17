import unittest
import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.recommendations_engine import RecommendationEngine
from privacy_protocol.recommendations_data import REC_ID_OPT_OUT_DATA_SELLING, REC_ID_REVIEW_THIRD_PARTY_POLICIES, REC_ID_MANAGE_COOKIES

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

if __name__ == '__main__':
    unittest.main()
