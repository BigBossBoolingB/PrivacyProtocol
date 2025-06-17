import unittest
import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.ml_classifier import ClauseClassifier
from privacy_protocol.clause_categories import CLAUSE_CATEGORIES

class TestClauseClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = ClauseClassifier()

    def test_predict_data_collection(self):
        text = "We collect your name and email address when you register."
        self.assertEqual(self.classifier.predict(text), 'Data Collection')

    def test_predict_data_sharing(self):
        text = "Information may be shared with third-party service providers."
        self.assertEqual(self.classifier.predict(text), 'Data Sharing')

    def test_predict_data_usage(self):
        text = "We use your data to personalize your experience."
        # This will likely fail with the current simple regex; the regex needs 'use your data' or similar
        # For now, let's test the current behavior. If it's 'Other', the test reflects that.
        # The current rule is r'uses? data', so "use your data" might not match.
        # Let's check ml_classifier.py rules: r'uses? data' - this should actually match "use your data"
        self.assertEqual(self.classifier.predict(text), 'Data Usage')


    def test_predict_user_rights(self):
        text = "You have the right to access or delete your information."
        self.assertEqual(self.classifier.predict(text), 'User Rights')

    def test_predict_security(self):
        text = "We implement security measures to protect your data."
        self.assertEqual(self.classifier.predict(text), 'Security')

    def test_predict_cookies(self):
        text = "Our website uses cookies for analytics."
        self.assertEqual(self.classifier.predict(text), 'Cookies and Tracking Technologies')

    def test_predict_policy_change(self):
        text = "We will notify you of changes to this policy."
        self.assertEqual(self.classifier.predict(text), 'Policy Change')

    def test_predict_default_other(self):
        text = "This is a generic statement with no specific keywords."
        self.assertEqual(self.classifier.predict(text), 'Other')

    def test_predict_empty_string(self):
        self.assertEqual(self.classifier.predict(""), 'Other')

    def test_predict_none_input(self):
        self.assertEqual(self.classifier.predict(None), 'Other')

    def test_all_rule_categories_are_valid(self):
        # This test ensures that all categories defined in classifier rules are valid
        for category_key, _ in self.classifier.rules:
            self.assertIn(category_key, CLAUSE_CATEGORIES)

if __name__ == '__main__':
    unittest.main()
