import unittest
import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.plain_language_translator import PlainLanguageTranslator
# Import CLAUSE_CATEGORIES to test all of them
from privacy_protocol.clause_categories import CLAUSE_CATEGORIES

class TestPlainLanguageTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = PlainLanguageTranslator()

    def test_translate_known_category_data_collection(self):
        summary = self.translator.translate("Clause text here", "Data Collection")
        self.assertIn("describes what personal information the company collects", summary)

    def test_translate_known_category_data_sharing(self):
        summary = self.translator.translate("Clause text here", "Data Sharing")
        self.assertIn("details if and how your information is shared", summary)

    def test_translate_unknown_category(self):
        summary = self.translator.translate("Clause text here", "MadeUpCategory123")
        self.assertEqual(summary, self.translator.default_summary)

    def test_translate_other_category(self):
        # 'Other' category should also use the default summary if not explicitly defined
        # or could have its own specific summary if added to dummy_explanations
        if 'Other' in self.translator.dummy_explanations:
            expected_summary = self.translator.dummy_explanations['Other']
        else:
            expected_summary = self.translator.default_summary
        summary = self.translator.translate("Clause text here", "Other")
        self.assertEqual(summary, expected_summary)

    def test_translate_none_category(self):
        summary = self.translator.translate("Clause text here", None)
        self.assertEqual(summary, self.translator.default_summary)

    def test_translate_integer_category(self):
        summary = self.translator.translate("Clause text here", 123)
        self.assertEqual(summary, self.translator.default_summary)

    def test_all_defined_categories_have_summaries_or_use_default(self):
        # This test ensures that every category in CLAUSE_CATEGORIES gets some response
        # (either specific or default) and doesn't cause an error.
        for category in CLAUSE_CATEGORIES:
            summary = self.translator.translate("Some clause text", category)
            self.assertIsInstance(summary, str)
            if category in self.translator.dummy_explanations:
                self.assertEqual(summary, self.translator.dummy_explanations[category])
            else:
                self.assertEqual(summary, self.translator.default_summary)

if __name__ == '__main__':
    unittest.main()
