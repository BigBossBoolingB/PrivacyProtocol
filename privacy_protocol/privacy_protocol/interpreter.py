import json
import spacy
import os
from .ml_classifier import ClauseClassifier
from .plain_language_translator import PlainLanguageTranslator # Import PlainLanguageTranslator

class PrivacyInterpreter:
    def __init__(self):
        self.keywords_data = {}
        self.nlp = None
        self.user_preferences = None # Add this
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("---")
            print("spaCy 'en_core_web_sm' model not found. Please download it by running:")
            print("python -m spacy download en_core_web_sm")
            print("Clause detection feature will be disabled until the model is available.")
            print("---")

        self.clause_classifier = ClauseClassifier()
        self.clause_classifier.load_model()

        self.plain_language_translator = PlainLanguageTranslator()
        self.plain_language_translator.load_model() # Currently a no-op

    def load_user_preferences(self, preferences_data):
        """Loads user preferences into the interpreter."""
        self.user_preferences = preferences_data

    def load_keywords_from_path(self, keywords_file_path):
        try:
            with open(keywords_file_path, 'r') as f:
                self.keywords_data = json.load(f)
        except FileNotFoundError:
            # This print is mostly for CLI debugging, could be a log entry in a web app
            # print(f"Error: Keywords file not found at {keywords_file_path}")
            self.keywords_data = {} # Ensure it's empty if file not found
        except json.JSONDecodeError:
            # print(f"Error: Could not decode JSON from {keywords_file_path}")
            self.keywords_data = {} # Ensure it's empty if corrupt

    def analyze_text(self, text):
        analyzed_sentences = []
        if not self.nlp:
            # print("Warning: spaCy model not loaded. Clause detection is disabled.")
            return analyzed_sentences

        if not text or not isinstance(text, str) or not text.strip():
            return analyzed_sentences

        doc = self.nlp(text)

        for sentence in doc.sents:
            sentence_text = sentence.text.strip()
            if not sentence_text:
                continue

            ai_category = self.clause_classifier.predict(sentence_text)
            current_keyword_matches = []
            sentence_lower = sentence_text.lower()

            for keyword, data in self.keywords_data.items():
                keyword_lower = keyword.lower()
                keyword_indices = [i for i in range(len(sentence_lower)) if sentence_lower.startswith(keyword_lower, i)]

                for keyword_index in keyword_indices:
                    is_negated = False
                    negation_words = ["not", "no", "never", "don't", "can't", "won't", "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't", "hadn't", "doesn't", "didn't", "shouldn't", "wouldn't", "couldn't"]

                    no_keyword_phrase_prefix = "no "
                    if keyword_index >= len(no_keyword_phrase_prefix) and \
                       sentence_lower.startswith(no_keyword_phrase_prefix, keyword_index - len(no_keyword_phrase_prefix)):
                        if (keyword_index - len(no_keyword_phrase_prefix) == 0) or \
                           (sentence_lower[keyword_index - len(no_keyword_phrase_prefix) - 1].isspace()):
                            is_negated = True

                    if not is_negated:
                        # Corrected window logic from previous step (use only one window_start)
                        window_start = max(0, keyword_index - 20)
                        text_immediately_before = sentence_lower[window_start:keyword_index].strip()
                        words_in_window = text_immediately_before.split()

                        if words_in_window:
                            for neg_word in negation_words:
                                if neg_word == "no": continue
                                if words_in_window[-1] == neg_word or \
                                   (len(words_in_window) > 1 and words_in_window[-2] == neg_word):
                                    is_negated = True
                                    break

                    if not is_negated:
                        already_added_this_keyword = any(
                            match["keyword"] == keyword for match in current_keyword_matches
                        )
                        if not already_added_this_keyword:
                            current_keyword_matches.append({
                                "keyword": keyword,
                                "explanation": data.get("explanation", "No explanation available."),
                                "category": data.get("category", "Uncategorized")
                            })
                        break

            summary = self.plain_language_translator.translate(sentence_text, ai_category)

            # Determine user_concern_level
            user_concern_level = 'None' # Default
            has_findings = (ai_category != 'Other') or bool(current_keyword_matches)

            if self.user_preferences: # Only apply if preferences are loaded
                # AI Category Checks
                if ai_category == 'Data Selling' and not self.user_preferences.get('data_selling_allowed', True):
                    user_concern_level = 'High'
                elif ai_category == 'Data Sharing' and not self.user_preferences.get('data_sharing_for_ads_allowed', True) and user_concern_level != 'High':
                    # Simplified: considering any 'Data Sharing' if ads sharing is disallowed.
                    # A more granular AI category (e.g., 'Data Sharing for Advertising') would be better.
                    user_concern_level = 'High'
                elif ai_category == 'Cookies and Tracking Technologies' and not self.user_preferences.get('cookies_for_tracking_allowed', True) and user_concern_level != 'High':
                    user_concern_level = 'High'
                elif ai_category == 'Childrens Privacy' and self.user_preferences.get('childrens_privacy_strict', False) and user_concern_level != 'High':
                    user_concern_level = 'High'
                elif ai_category == 'Policy Change' and self.user_preferences.get('policy_changes_notification_required', False) and user_concern_level != 'High':
                    user_concern_level = 'Medium'

                # Keyword Match Checks (can elevate concern)
                # This is a basic example; can be more sophisticated
                for kw_match in current_keyword_matches:
                    if kw_match['category'] == 'Data Selling' and not self.user_preferences.get('data_selling_allowed', True):
                        user_concern_level = 'High'
                        break
                    # Add more keyword-category to preference checks if needed

            if user_concern_level == 'None' and has_findings:
                user_concern_level = 'Low'

            analyzed_sentences.append({
                "clause_text": sentence_text,
                "ai_category": ai_category,
                "keyword_matches": current_keyword_matches,
                "plain_language_summary": summary,
                "user_concern_level": user_concern_level
            })

        return analyzed_sentences

    def calculate_risk_assessment(self, analyzed_sentences_data):
        overall_risk_score = 0
        high_concern_count = 0
        medium_concern_count = 0
        low_concern_count = 0
        none_concern_count = 0 # Optional, for completeness

        if not analyzed_sentences_data:
            return {
                'overall_risk_score': 0,
                'high_concern_count': 0,
                'medium_concern_count': 0,
                'low_concern_count': 0,
                'none_concern_count': 0
            }

        for sentence_analysis in analyzed_sentences_data:
            concern_level = sentence_analysis.get('user_concern_level', 'None') # Default to 'None'
            if concern_level == 'High':
                overall_risk_score += 10
                high_concern_count += 1
            elif concern_level == 'Medium':
                overall_risk_score += 5
                medium_concern_count += 1
            elif concern_level == 'Low':
                overall_risk_score += 1
                low_concern_count += 1
            else: # 'None'
                none_concern_count +=1

        return {
            'overall_risk_score': overall_risk_score,
            'high_concern_count': high_concern_count,
            'medium_concern_count': medium_concern_count,
            'low_concern_count': low_concern_count,
            'none_concern_count': none_concern_count
        }

if __name__ == '__main__':
    from .user_preferences import get_default_preferences # For __main__ example

    script_dir = os.path.dirname(__file__)
    keywords_path = os.path.join(script_dir, '..', 'data', 'keywords.json')
    print(f"Info: Attempting to load keywords for __main__ execution from: {keywords_path}")

    interpreter = PrivacyInterpreter()

    # Load sample preferences for the __main__ example
    sample_prefs = get_default_preferences()
    sample_prefs['data_selling_allowed'] = False
    sample_prefs['cookies_for_tracking_allowed'] = False
    interpreter.load_user_preferences(sample_prefs)
    print(f"Info: Loaded sample user preferences for __main__: {sample_prefs}")


    if interpreter.nlp is None:
        print("Exiting example: spaCy model 'en_core_web_sm' not loaded or available.")
    else:
        interpreter.load_keywords_from_path(keywords_path)
        if not interpreter.keywords_data:
            print(f"Exiting example: Keywords not loaded from {keywords_path}. Check path and file content.")
        else:
            sample_text = (
                "We collect your personal data for service provision. "
                "We do not sell your data. " # AI: Data Selling, Keyword: (none due to negation) -> Concern: High (if data_selling_allowed=false)
                "However, we may share your information with trusted third-party service providers for analytics. " # AI: Data Sharing -> Concern: Low (if data_sharing_for_ads_allowed=false but this is analytics)
                "You have the right to access your data. " # AI: User Rights -> Concern: Low
                "We use cookies for tracking purposes and site functionality. " # AI: Cookies/Tracking, Keyword: cookies, tracking -> Concern: High (if cookies_for_tracking_allowed=false)
                "This policy might change. Our contact is policy@example.com." # AI: Policy Change -> Concern: Medium (if policy_changes_notification_required=true)
            )
            print(f"\nAnalyzing sample text:\n------------------------\n{sample_text}\n------------------------\n")

            analysis_results = interpreter.analyze_text(sample_text)

            if analysis_results:
                print("\n--- Analysis Results (Interpreter Example) ---")
                for sentence_analysis in analysis_results:
                    print(f"\nSentence: \"{sentence_analysis['clause_text']}\"")
                    print(f"  AI Category: {sentence_analysis['ai_category']}")
                    print(f"  Plain Summary: {sentence_analysis['plain_language_summary']}")
                    print(f"  User Concern Level: {sentence_analysis['user_concern_level']}")
                    if sentence_analysis['keyword_matches']:
                        print("  Keyword Matches:")
                        for match in sentence_analysis['keyword_matches']:
                            print(f"    - Keyword: {match['keyword']}")
                            print(f"      Category (from keyword list): {match['category']}")
                            print(f"      Explanation: {match['explanation']}")
                    else:
                        print("  No keyword matches in this sentence.")

                # Calculate and print risk assessment
                risk_assessment = interpreter.calculate_risk_assessment(analysis_results)
                print("\n\n--- Risk Assessment (Interpreter Example) ---")
                print(f"Overall Risk Score: {risk_assessment['overall_risk_score']}")
                print(f"High Concern Sentences: {risk_assessment['high_concern_count']}")
                print(f"Medium Concern Sentences: {risk_assessment['medium_concern_count']}")
                print(f"Low Concern Sentences: {risk_assessment['low_concern_count']}")
                print(f"None Concern Sentences: {risk_assessment['none_concern_count']}")
            else:
                print("No analysis results from the interpreter example (this might also happen if NLP model is missing).")
