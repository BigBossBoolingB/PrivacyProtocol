import unittest
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import app # Flask app instance from privacy_protocol/app.py

# Determine if spaCy model is available (reuse or adapt logic from test_interpreter)
SPACY_MODEL_AVAILABLE = False
NLP_UNAVAILABLE_MESSAGE_IN_RESULTS = "NLP model 'en_core_web_sm' was not loaded" # Part of the message in results.html
try:
    import spacy
    # Try to load the model to confirm it's actually available and not just the library
    spacy.load("en_core_web_sm")
    SPACY_MODEL_AVAILABLE = True
    print("test_app.py: spaCy model 'en_core_web_sm' IS available.", file=sys.stderr)
except ImportError:
    print("test_app.py: spaCy library not installed. Some web tests will be skipped.", file=sys.stderr)
except OSError:
    print("test_app.py: spaCy model 'en_core_web_sm' not found. Some web tests will be skipped.", file=sys.stderr)


class TestWebApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms
        self.client = app.test_client()

        # Ensure keywords are loaded in the app's interpreter instance for tests
        # This assumes app.interpreter is the PrivacyInterpreter instance
        # and that KEYWORDS_FILE_PATH is accessible/correctly set in app.py
        # If app.interpreter.keywords_data is empty, web tests requiring keywords will fail.
        if not app.interpreter.keywords_data:
             print("WARNING (test_app.py setUp): Keywords not loaded in app.interpreter.", file=sys.stderr)
             # Attempt to load them if path is known, for robustness, though app.py should handle this.
             # keywords_path_for_test = os.path.join(project_root, 'data', 'keywords.json')
             # app.interpreter.load_keywords_from_path(keywords_path_for_test)


    def test_main_page_loads(self):
        """Test if the main page (index.html) loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Privacy Policy Analyzer", response.data)
        self.assertIn(b"Paste Privacy Policy Text:", response.data)
        self.assertIn(b'<textarea name="policy_text"', response.data)
        self.assertIn(b'<input type="submit" value="Analyze Policy">', response.data)

    def test_analyze_page_empty_input(self):
        """Test the /analyze endpoint with empty policy_text."""
        response = self.client.post('/analyze', data={'policy_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No concerning keywords found, the input was empty", response.data)
        # Also check that the original text area shows "No text submitted" or similar
        self.assertIn(b"No text submitted.", response.data)


    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available for this test.")
    def test_analyze_page_with_data_and_nlp_model(self):
        """Test /analyze with text containing keywords, assuming NLP model is available."""
        sample_text = "We share your data with third-party advertising partners for tracking purposes."
        response = self.client.post('/analyze', data={'policy_text': sample_text})
        self.assertEqual(response.status_code, 200)

        # Check for original policy text
        self.assertIn(sample_text.encode(), response.data)

        # Check for keyword "third-party"
        self.assertIn(b"<h3>Keyword Found: third-party</h3>", response.data)
        self.assertIn(b"<p><strong>Category:</strong> Data Sharing</p>", response.data)
        self.assertIn(b"<p><strong>Explanation:</strong>", response.data) # Check for start of explanation line
        self.assertIn(b'<p><strong>Clause Text:</strong> "' + sample_text.encode() + b'"</p>', response.data)

        # Check for keyword "tracking"
        self.assertIn(b"<h3>Keyword Found: tracking</h3>", response.data)
        self.assertIn(b"<p><strong>Category:</strong> User Activity Monitoring</p>", response.data)
        self.assertIn(b'<p><strong>Clause Text:</strong> "' + sample_text.encode() + b'"</p>', response.data)


    @unittest.skipUnless(SPACY_MODEL_AVAILABLE, "spaCy model 'en_core_web_sm' not available for this test.")
    def test_analyze_page_with_negated_keyword_and_nlp_model(self):
        """Test /analyze with text containing a negated keyword, assuming NLP model is available."""
        sample_text = "We do not sell data ever. Our commitment is to your privacy."
        response = self.client.post('/analyze', data={'policy_text': sample_text})
        self.assertEqual(response.status_code, 200)

        self.assertIn(sample_text.encode(), response.data)

        # "data selling" should NOT be flagged
        self.assertNotIn(b"Keyword Found: data selling", response.data)
        # Depending on other keywords, either "No concerning keywords" or other keywords might appear.
        # For this specific text, assuming "data selling" is the only relevant keyword from keywords.json:
        if b"Keyword Found:" not in response.data: # Check if NO keywords were flagged at all
             self.assertIn(b"No concerning keywords found", response.data)


    @unittest.skipIf(SPACY_MODEL_AVAILABLE, "spaCy model IS available, skipping test for NLP unavailable scenario.")
    def test_analyze_page_no_nlp_model(self):
        """Test /analyze when the NLP model is unavailable."""
        sample_text = "This is some policy text with third-party."
        response = self.client.post('/analyze', data={'policy_text': sample_text})
        self.assertEqual(response.status_code, 200)

        # Check that the specific message about NLP model unavailability is shown
        self.assertIn(NLP_UNAVAILABLE_MESSAGE_IN_RESULTS.encode(), response.data,
                      "Message about NLP model unavailability not found in response.")
        # Keywords might still be found if the fallback is simple keyword spotting,
        # or no keywords if analyze_text returns empty when NLP is missing.
        # Current interpreter.py returns empty if NLP model is missing.
        self.assertIn(b"No concerning keywords found", response.data)


if __name__ == '__main__':
    unittest.main()
