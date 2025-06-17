from .clause_categories import CLAUSE_CATEGORIES
import re

class ClauseClassifier:
    def __init__(self):
        # In a real scenario, this is where a trained model would be loaded.
        # For this dummy classifier, we define simple rules.
        self.rules = [
            # Category, Keywords (case-insensitive, whole word match preferred where possible)
            ('Data Collection', [r'collects?', r'gathers?', r'receives?', r'obtains?', r'information you provide', r'automatically collected']),
            ('Data Sharing', [r'shares?', r'discloses?', r'third-part(y|ies)', r'partners?', r'vendors?', r'service providers?', r'transfers? data']),
            ('Data Selling', [r'data\s+selling', r'sell\s+(your|our|the)?\s*data']),
            ('Data Usage', [r'use(s)?\s+(your|our|the)?\s*data', r'process(es)?\s+(your|our|the)?\s*data', r'purpose of', r'how we use', r'utilizes?']),
            ('User Rights', [r'your\s+rights?', r'right\s+to\s+access', r'right\s+to\s+correct', r'right\s+to\s+delete', r'access\s+(your|our|the)?\s*data', r'correct\s+(your|our|the)?\s*data', r'delete\s+(your|our|the)?\s*data', r'data\s+portability', r'opt-out', r'choices']),
            ('Security', [r'security', r'protects?', r'safeguards?', r'encryption', r'measures? to protect']),
            ('Data Retention', [r'retains? data', r'how long we keep', r'data storage period', r'deletion of data']),
            ('Consent/Opt-out', [r'consent', r'opt-out', r'unsubscribe', r'your choices', r'withdraw consent']),
            ('Policy Change', [r'changes to this policy', r'updates to this policy', r'policy amendments?', r'notification of changes']),
            ('International Data Transfer', [r'international transfers?', r'data across borders', r'cross-border', r'outside your country']),
            ('Childrens Privacy', [r'childrens? privacy', r'under the age of', r'minors?']),
            ('Contact Information', [r'contact us', r'questions about this policy', r'data protection officer', r'email us']),
            ('Cookies and Tracking Technologies', [r'cookies?', r'web beacons?', r'tracking technologies', r'pixels?', r'ad identifiers?', r'tracking'])
        ]
        self.default_category = 'Other'
        # Ensure all rule categories are valid
        for category, _ in self.rules:
            if category not in CLAUSE_CATEGORIES:
                raise ValueError(f"Invalid category in ClauseClassifier rules: {category}. Must be one of {CLAUSE_CATEGORIES}")

    def load_model(self):
        # Placeholder method for future actual model loading
        print("Dummy ClauseClassifier: Model loaded (placeholder - using rule-based logic).")

    def predict(self, clause_text: str) -> str:
        if not clause_text or not isinstance(clause_text, str):
            return self.default_category

        lower_text = clause_text.lower()
        for category, patterns in self.rules:
            for pattern in patterns:
                # Using re.search for flexibility (e.g., handling plurals with 's?')
                # Adding word boundaries (\b) to some patterns could make them more precise
                # e.g., r'\bcollects?\b' to avoid matching 'recollects'
                # For simplicity here, direct regex search is used.
                # A more robust approach would be to pre-compile regexes in __init__.
                if re.search(pattern, lower_text):
                    return category
        return self.default_category

if __name__ == '__main__':
    # Example Usage
    classifier = ClauseClassifier()
    classifier.load_model()

    test_clauses = [
        "We collect your name and email address.",
        "We may share your information with trusted third-party service providers.",
        "We use your data to improve our services.",
        "You have the right to access your personal data.",
        "This policy may be updated periodically.",
        "We use cookies to enhance your browsing experience.",
        "This is a general statement."
    ]

    print("\n--- Dummy Classifier Predictions ---")
    for clause in test_clauses:
        prediction = classifier.predict(clause)
        print(f"Clause: {clause}")
        print(f"Predicted Category: {prediction}\n")
