import json
import spacy
import os
from .ml_classifier import ClauseClassifier # Import ClauseClassifier

class PrivacyInterpreter:
    def __init__(self):
        self.keywords_data = {}
        self.nlp = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("---")
            print("spaCy 'en_core_web_sm' model not found. Please download it by running:")
            print("python -m spacy download en_core_web_sm")
            print("Clause detection feature will be disabled until the model is available.")
            print("---")

        self.clause_classifier = ClauseClassifier()
        self.clause_classifier.load_model() # Prints a message for dummy model

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

            analyzed_sentences.append({
                "clause_text": sentence_text,
                "ai_category": ai_category,
                "keyword_matches": current_keyword_matches
            })

        return analyzed_sentences

if __name__ == '__main__':
    # This block is for basic, direct testing of the interpreter.
    # Assumes being run from the 'privacy_protocol/privacy_protocol' directory.
    script_dir = os.path.dirname(__file__)
    # Path relative to this script to reach project_root/data/keywords.json
    # Corrected path: from privacy_protocol/privacy_protocol, go up one level to privacy_protocol/, then data/
    keywords_path = os.path.join(script_dir, '..', 'data', 'keywords.json')

    # The print below is for the __main__ block's own feedback, not a class diagnostic
    print(f"Info: Attempting to load keywords for __main__ execution from: {keywords_path}")

    interpreter = PrivacyInterpreter()

    if interpreter.nlp is None:
        print("Exiting example: spaCy model 'en_core_web_sm' not loaded or available.")
    else:
        interpreter.load_keywords_from_path(keywords_path)
        if not interpreter.keywords_data:
            print(f"Exiting example: Keywords not loaded from {keywords_path}. Check path and file content.")
        else:
            sample_text = (
                "We collect your personal data for service provision. "
                "We do not sell your data. "
                "However, we may share your information with trusted third-party service providers for analytics. "
                "You have the right to access your data. "
                "We use cookies for tracking purposes and site functionality. "
                "This policy might change. Our contact is policy@example.com."
            )
            print(f"\nAnalyzing sample text:\n------------------------\n{sample_text}\n------------------------\n")

            analysis_results = interpreter.analyze_text(sample_text)

            if analysis_results:
                print("\n--- Analysis Results (Interpreter Example) ---")
                for sentence_analysis in analysis_results:
                    print(f"\nSentence: \"{sentence_analysis['clause_text']}\"")
                    print(f"  AI Category: {sentence_analysis['ai_category']}")
                    if sentence_analysis['keyword_matches']:
                        print("  Keyword Matches:")
                        for match in sentence_analysis['keyword_matches']:
                            print(f"    - Keyword: {match['keyword']}")
                            print(f"      Category (from keyword list): {match['category']}")
                            print(f"      Explanation: {match['explanation']}")
                    else:
                        print("  No keyword matches in this sentence.")
            else:
                print("No analysis results from the interpreter example (this might also happen if NLP model is missing).")
