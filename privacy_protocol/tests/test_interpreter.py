import unittest
import json
import os
import sys

# Add the project root to the Python path to allow importing privacy_protocol
# This assumes 'tests' is a subdirectory of the project root.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol.interpreter import PrivacyInterpreter

class TestPrivacyInterpreter(unittest.TestCase):

    def setUp(self):
        # Create a temporary keywords file for testing
        self.keywords_data = {
            "third-party": {
                "explanation": "Test explanation for third-party.",
                "category": "Data Sharing"
            },
            "data selling": {
                "explanation": "Test explanation for data selling.",
                "category": "Data Selling"
            },
            "tracking": {
                "explanation": "Test explanation for tracking.",
                "category": "User Activity Monitoring"
            }
        }
        self.temp_keywords_file = "temp_keywords.json"
        with open(self.temp_keywords_file, 'w') as f:
            json.dump(self.keywords_data, f)

        self.interpreter = PrivacyInterpreter()
        self.interpreter.load_keywords_from_path(self.temp_keywords_file)

    def tearDown(self):
        # Remove the temporary keywords file
        if os.path.exists(self.temp_keywords_file):
            os.remove(self.temp_keywords_file)

    def test_keyword_loading(self):
        self.assertIsNotNone(self.interpreter.keywords_data)
        self.assertEqual(len(self.interpreter.keywords_data), 3)
        self.assertIn("third-party", self.interpreter.keywords_data)

    def test_analyze_text_no_keywords(self):
        text = "This policy is clean and respects user privacy."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 0)

    def test_analyze_text_with_one_keyword(self):
        text = "We may share your information with a third-party."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["keyword"], "third-party")
        self.assertEqual(results[0]["explanation"], "Test explanation for third-party.")
        self.assertEqual(results[0]["category"], "Data Sharing")

    def test_analyze_text_with_multiple_keywords(self):
        text = "Our policy on data selling and tracking is clear."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 2)

        # Check for data selling
        found_data_selling = any(item['keyword'] == 'data selling' for item in results)
        self.assertTrue(found_data_selling)

        # Check for tracking
        found_tracking = any(item['keyword'] == 'tracking' for item in results)
        self.assertTrue(found_tracking)

        for item in results:
            if item['keyword'] == 'data selling':
                self.assertEqual(item['explanation'], "Test explanation for data selling.")
                self.assertEqual(item['category'], "Data Selling")
            elif item['keyword'] == 'tracking':
                self.assertEqual(item['explanation'], "Test explanation for tracking.")
                self.assertEqual(item['category'], "User Activity Monitoring")


    def test_analyze_text_keyword_case_insensitivity(self):
        text = "This policy mentions Third-Party services."
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["keyword"], "third-party") # Keyword should be stored in its original case

    def test_analyze_text_empty_text(self):
        text = ""
        results = self.interpreter.analyze_text(text)
        self.assertEqual(len(results), 0)

    def test_keyword_missing_explanation_or_category(self):
        # Overwrite keywords data for this specific test
        keywords_missing_data = {
            "new_keyword": {}
        }
        temp_missing_file = "temp_missing_keywords.json"
        with open(temp_missing_file, 'w') as f:
            json.dump(keywords_missing_data, f)

        interpreter_missing = PrivacyInterpreter()
        interpreter_missing.load_keywords_from_path(temp_missing_file)

        text = "This policy has a new_keyword."
        results = interpreter_missing.analyze_text(text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["keyword"], "new_keyword")
        self.assertEqual(results[0]["explanation"], "No explanation available.")
        self.assertEqual(results[0]["category"], "Uncategorized")

        if os.path.exists(temp_missing_file):
            os.remove(temp_missing_file)

    def test_nonexistent_keywords_file(self):
        # Test initialization with a non-existent file
        # Suppress print output for this test
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

        interpreter_nonexistent = PrivacyInterpreter()
        interpreter_nonexistent.load_keywords_from_path("nonexistent_keywords.json")

        sys.stdout.close()
        sys.stdout = original_stdout # Restore stdout

        self.assertEqual(interpreter_nonexistent.keywords_data, {})
        # Attempting to analyze with no keywords should yield no results
        results = interpreter_nonexistent.analyze_text("Some text.")
        self.assertEqual(len(results), 0)

    def test_corrupted_keywords_file(self):
        # Create a corrupted JSON file
        corrupted_file = "corrupted_keywords.json"
        with open(corrupted_file, 'w') as f:
            f.write("this is not valid json")

        # Suppress print output for this test
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

        interpreter_corrupted = PrivacyInterpreter()
        interpreter_corrupted.load_keywords_from_path(corrupted_file)

        sys.stdout.close()
        sys.stdout = original_stdout # Restore stdout

        self.assertEqual(interpreter_corrupted.keywords_data, {})
        results = interpreter_corrupted.analyze_text("Some text.")
        self.assertEqual(len(results), 0)

        if os.path.exists(corrupted_file):
            os.remove(corrupted_file)


if __name__ == '__main__':
    unittest.main()
