import json
import spacy
import os

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
        # No critical error if model is not found, features will be degraded.

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
        flagged_clauses = []
        if not self.nlp:
            # Fallback or warning if spaCy model isn't loaded
            # For now, if no NLP, we can't do sentence-based clause detection.
            # One could implement a simpler keyword spotter here as a fallback,
            # but the current plan step implies upgrading to NLP.
            # So, if no NLP, return empty results for this feature.
            # print("Warning: spaCy model not loaded. Clause detection is disabled.")
            return flagged_clauses

        if not text or not isinstance(text, str) or not text.strip():
            return flagged_clauses

        doc = self.nlp(text)

        for sentence in doc.sents:
            sentence_text = sentence.text.strip() # Use stripped sentence text
            if not sentence_text: # Skip empty sentences if any
                continue
            sentence_lower = sentence_text.lower()
            for keyword, data in self.keywords_data.items():
                keyword_lower = keyword.lower()

                # Find all occurrences of the keyword in the sentence
                keyword_indices = [i for i in range(len(sentence_lower)) if sentence_lower.startswith(keyword_lower, i)]

                for keyword_index in keyword_indices:
                    is_negated = False
                    negation_words = ["not", "no", "never", "don't", "can't", "won't", "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't", "hadn't", "doesn't", "didn't", "shouldn't", "wouldn't", "couldn't"]

                    # Check 1: Specific "no <keyword>" pattern (e.g., "no data selling")
                    # Ensure "no " is directly before the keyword and is preceded by a space or is at sentence start.
                    no_keyword_phrase_prefix = "no "
                    if keyword_index >= len(no_keyword_phrase_prefix) and \
                       sentence_lower.startswith(no_keyword_phrase_prefix, keyword_index - len(no_keyword_phrase_prefix)):
                        # Check if "no" is a whole word, i.e., preceded by a space or sentence start
                        if (keyword_index - len(no_keyword_phrase_prefix) == 0) or \
                           (sentence_lower[keyword_index - len(no_keyword_phrase_prefix) - 1].isspace()):
                            is_negated = True

                    # Check 2: Other negations in a small window immediately before the keyword
                    if not is_negated:
                        # Window of ~15 chars immediately before the keyword
                        window_start = max(0, keyword_index - 15)
                        text_immediately_before = sentence_lower[window_start:keyword_index].strip()

                        # Window of ~20 chars immediately before the keyword to capture 2-3 words
                        window_start = max(0, keyword_index - 20)
                        text_immediately_before = sentence_lower[window_start:keyword_index].strip()
                        words_in_window = text_immediately_before.split()

                        if words_in_window:
                            for neg_word in negation_words:
                                if neg_word == "no": continue # Already handled by "no <keyword>"
                                # Check if the negation word is one of the last two words in the window
                                if words_in_window[-1] == neg_word or \
                                   (len(words_in_window) > 1 and words_in_window[-2] == neg_word):
                                    is_negated = True
                                    break

                    if not is_negated:
                        # Avoid adding the same sentence for the same keyword multiple times if keyword appears more than once non-negated
                        already_flagged_for_sentence_keyword = any(
                            fc["clause_text"] == sentence_text and fc["keyword"] == keyword for fc in flagged_clauses
                        )
                        if not already_flagged_for_sentence_keyword:
                            flagged_clauses.append({
                                "keyword": keyword,
                                "explanation": data.get("explanation", "No explanation available."),
                                "category": data.get("category", "Uncategorized"),
                                "clause_text": sentence_text
                            })
                        # Since we flag a sentence once per keyword type, even if the keyword appears multiple times non-negated,
                        # we can break after the first non-negated finding for this specific keyword.
                        break
        return flagged_clauses

if __name__ == '__main__':
    # This block is for basic, direct testing of the interpreter.
    # Assumes being run from the 'privacy_protocol/privacy_protocol' directory.
    script_dir = os.path.dirname(__file__)
    # Path relative to this script to reach project_root/data/keywords.json
    keywords_path = os.path.join(script_dir, '..', '..', 'data', 'keywords.json')

    print(f"Attempting to load keywords from: {keywords_path}")

    interpreter = PrivacyInterpreter() # NLP model loading message will appear here if model is missing

    if interpreter.nlp is None:
        print("Exiting example: spaCy model 'en_core_web_sm' not loaded or available.")
    else:
        interpreter.load_keywords_from_path(keywords_path)
        if not interpreter.keywords_data:
            print(f"Exiting example: Keywords not loaded from {keywords_path}. Check path and file content.")
        else:
            sample_text = (
                "This is the first sentence. We may share your data with a third-party for analytics. "
                "This is a sentence about data selling. We use cookies for tracking purposes. "
                "This is the final sentence. Anonymized data is also used."
            )
            print(f"Analyzing sample text:\n{sample_text}\n")
            analysis_results = interpreter.analyze_text(sample_text)
            if analysis_results:
                print("\n--- Analysis Results (Interpreter Example) ---")
                for item in analysis_results:
                    print(f"Keyword: {item['keyword']}")
                    print(f"Category: {item['category']}")
                    print(f"Explanation: {item['explanation']}")
                    print(f"Clause Text: {item['clause_text']}\n")
            else:
                print("No concerning keywords found in the sample text by the interpreter example.")
