import json
import spacy
import os
from .ml_classifier import ClauseClassifier
from .plain_language_translator import PlainLanguageTranslator # Import PlainLanguageTranslator

class PrivacyInterpreter:
    # Define base points and bonuses for service_risk_score calculation
    AI_CATEGORY_BASE_POINTS = {
        'Data Selling': 20,
        'Data Sharing': 15,
        'Cookies and Tracking Technologies': 10,
        'Childrens Privacy': 15,
        'Data Collection': 10,
        'Security': 0,
        'Data Retention': 5,
        'Policy Change': 5,
        'User Rights': 10,
        'International Data Transfer': 5,
        'Contact Information': 0,
        'Consent/Opt-out': 10,
        'Other': 1
    }
    USER_CONCERN_BONUS_POINTS = {
        'High': 15,
        'Medium': 7,
        'Low': 2,
        'None': 0
    }
    # Calculate MAX_RISK_POINTS_PER_SENTENCE based on the defined points
    # Ensure this calculation is done after AI_CATEGORY_BASE_POINTS and USER_CONCERN_BONUS_POINTS are defined.
    # One way is to do it directly here if Python's class attribute definition order allows direct reference,
    # or compute it within methods/constructor if needed. For simplicity, direct computation:
    _max_ai_base = 0
    for val in AI_CATEGORY_BASE_POINTS.values():
        if val > _max_ai_base:
            _max_ai_base = val
    MAX_RISK_POINTS_PER_SENTENCE = _max_ai_base + USER_CONCERN_BONUS_POINTS['High']


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
        none_concern_count = 0
        num_clauses_analyzed = len(analyzed_sentences_data)
        accumulated_risk_points_for_service_score = 0

        if num_clauses_analyzed == 0:
            return {
                'overall_risk_score': 0,
                'service_risk_score': 0,
                'high_concern_count': 0,
                'medium_concern_count': 0,
                'low_concern_count': 0,
                'none_concern_count': 0,
                'num_clauses_analyzed': 0
            }

        for sentence_analysis in analyzed_sentences_data:
            concern_level = sentence_analysis.get('user_concern_level', 'None')
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

            # New logic for service_risk_score
            ai_category = sentence_analysis.get('ai_category', 'Other')
            base_points = self.AI_CATEGORY_BASE_POINTS.get(ai_category, self.AI_CATEGORY_BASE_POINTS['Other'])
            concern_bonus = self.USER_CONCERN_BONUS_POINTS.get(concern_level, 0)
            sentence_actual_risk = base_points + concern_bonus
            accumulated_risk_points_for_service_score += sentence_actual_risk

        service_risk_score = 0
        if num_clauses_analyzed > 0:
            total_possible_risk_points_for_service_score = num_clauses_analyzed * self.MAX_RISK_POINTS_PER_SENTENCE
            if total_possible_risk_points_for_service_score > 0:
                service_risk_score = (accumulated_risk_points_for_service_score / total_possible_risk_points_for_service_score) * 100
            service_risk_score = round(min(max(service_risk_score, 0), 100))

        return {
            'overall_risk_score': overall_risk_score,
            'service_risk_score': service_risk_score,
            'high_concern_count': high_concern_count,
            'medium_concern_count': medium_concern_count,
            'low_concern_count': low_concern_count,
            'none_concern_count': none_concern_count,
            'num_clauses_analyzed': num_clauses_analyzed
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
                print(f"Overall Risk Score (sum of points): {risk_assessment['overall_risk_score']}")
                print(f"Service Risk Score (0-100 normalized): {risk_assessment['service_risk_score']}")
                print(f"High Concern Sentences: {risk_assessment['high_concern_count']}")
                print(f"Medium Concern Sentences: {risk_assessment['medium_concern_count']}")
                print(f"Low Concern Sentences: {risk_assessment['low_concern_count']}")
                print(f"None Concern Sentences: {risk_assessment['none_concern_count']}")
                print(f"Total Clauses Analyzed: {risk_assessment['num_clauses_analyzed']}")
            else:
                print("No analysis results from the interpreter example (this might also happen if NLP model is missing).")
