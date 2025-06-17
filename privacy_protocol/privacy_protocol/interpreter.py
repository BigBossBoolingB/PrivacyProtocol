import json

class PrivacyInterpreter:
    def __init__(self):
        self.keywords_data = {}

    def load_keywords_from_path(self, keywords_file_path):
        try:
            with open(keywords_file_path, 'r') as f:
                self.keywords_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Keywords file not found at {keywords_file_path}")
            self.keywords_data = {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {keywords_file_path}")
            self.keywords_data = {}


    def analyze_text(self, text):
        flagged_clauses = []
        text_lower = text.lower() # Case-insensitive matching

        for keyword, data in self.keywords_data.items():
            if keyword.lower() in text_lower:
                # Simple flagging: if keyword is present, flag it.
                # In a real app, this would involve more sophisticated sentence/clause boundary detection.
                # For now, we'll just indicate the keyword was found.
                flagged_clauses.append({
                    "keyword": keyword,
                    "explanation": data.get("explanation", "No explanation available."),
                    "category": data.get("category", "Uncategorized"),
                    # "clause_text": "Clause text would be extracted here in a more advanced version" # Placeholder
                })
        return flagged_clauses

if __name__ == '__main__':
    # Example Usage (for testing within this file)
    interpreter = PrivacyInterpreter() # Path for local testing
    interpreter.load_keywords_from_path('../data/keywords.json') # Load keywords for local testing
    if not interpreter.keywords_data:
        print("Exiting due to keyword loading error.")
    else:
        sample_text = """
        This is a sample privacy policy. We may share your data with a third-party for analytics.
        We will not engage in data selling. However, we use cookies for tracking purposes.
        Sometimes we use anonymized data for research.
        """
        analysis_results = interpreter.analyze_text(sample_text)
        if analysis_results:
            print("\n--- Analysis Results ---")
            for item in analysis_results:
                print(f"Keyword: {item['keyword']}")
                print(f"Category: {item['category']}")
                print(f"Explanation: {item['explanation']}\n")
        else:
            print("No concerning keywords found in the sample text.")
