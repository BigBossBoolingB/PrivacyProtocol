from .recommendations_data import RECOMMENDATIONS_DATA
# from .user_preferences import PREFERENCE_KEYS # May not be needed directly if relying on user_concern_level

class RecommendationEngine:
    def __init__(self):
        self.recommendation_rules = RECOMMENDATIONS_DATA
        # Pre-process or validate rules if necessary (e.g., ensure min_concern levels are valid)
        self._validate_rules()

    def _validate_rules(self):
        valid_concern_levels = ['High', 'Medium', 'Low', 'None']
        for rule in self.recommendation_rules:
            if not rule.get('id') or not rule.get('title') or not rule.get('text') or not rule.get('triggers'):
                raise ValueError(f"Invalid recommendation rule structure: {rule.get('id', 'Unknown ID')}")
            for trigger in rule['triggers']:
                if 'min_concern' in trigger:
                    if not isinstance(trigger['min_concern'], list):
                        raise ValueError(f"'min_concern' must be a list in rule {rule['id']}")
                    for level in trigger['min_concern']:
                        if level not in valid_concern_levels:
                            raise ValueError(f"Invalid concern level '{level}' in rule {rule['id']}")

    def generate_recommendations_for_sentence(self, sentence_analysis):
        """
        Generates recommendations for a single analyzed sentence.
        `sentence_analysis` is a dictionary for one sentence, containing:
            - 'ai_category'
            - 'user_concern_level'
            - 'keyword_matches' (list of dicts, each with 'category')
        """
        applicable_recommendations = []
        triggered_rec_ids = set() # To avoid duplicate recommendations for the same sentence

        ai_category = sentence_analysis.get('ai_category')
        user_concern = sentence_analysis.get('user_concern_level', 'None')

        for rule in self.recommendation_rules:
            if rule['id'] in triggered_rec_ids:
                continue # Already added this recommendation for this sentence

            for trigger in rule['triggers']:
                triggered = False
                # Check AI category trigger
                if 'ai_category' in trigger and trigger['ai_category'] == ai_category:
                    if 'min_concern' in trigger and user_concern in trigger['min_concern']:
                        triggered = True

                # Future: Check keyword category trigger (more complex if keywords have own categories)
                # For now, keyword_matches are not directly used by recommendation triggers in this basic version,
                # but they influence user_concern_level which is used.

                if triggered:
                    applicable_recommendations.append({
                        'id': rule['id'],
                        'title': rule['title'],
                        'text': rule['text']
                    })
                    triggered_rec_ids.add(rule['id'])
                    break # Move to next rule once this one is triggered for the sentence

        return applicable_recommendations

    def augment_analysis_with_recommendations(self, analyzed_sentences_data):
        """
        Augments each sentence analysis object in the list with a 'recommendations' key.
        Modifies `analyzed_sentences_data` in place.
        `user_preferences` are implicitly handled via `user_concern_level` in `analyzed_sentences_data`.
        """
        for sentence_analysis in analyzed_sentences_data:
            sentence_analysis['recommendations'] = self.generate_recommendations_for_sentence(sentence_analysis)
        return analyzed_sentences_data # Return modified data for clarity, though it's modified in-place

if __name__ == '__main__':
    engine = RecommendationEngine()
    print(f"RecommendationEngine initialized with {len(engine.recommendation_rules)} rules.")

    # Example sentence analysis data (simplified)
    sample_analyzed_sentences = [
        {
            'clause_text': 'We sell your personal data to advertisers.',
            'ai_category': 'Data Selling',
            'user_concern_level': 'High',
            'keyword_matches': [{'keyword': 'sell data', 'category': 'Data Selling Practices', 'explanation': '...'}]
        },
        {
            'clause_text': 'We use cookies for website functionality.',
            'ai_category': 'Cookies and Tracking Technologies',
            'user_concern_level': 'Low',
            'keyword_matches': []
        },
        {
            'clause_text': 'Our security measures are robust.',
            'ai_category': 'Security',
            'user_concern_level': 'Low',
            'keyword_matches': []
        },
         {
            'clause_text': 'This is another important sentence about data sharing.',
            'ai_category': 'Data Sharing',
            'user_concern_level': 'Medium',
            'keyword_matches': []
        }
    ]

    print("\n--- Generating Recommendations for Sample Sentences ---")
    augmented_data = engine.augment_analysis_with_recommendations(sample_analyzed_sentences)

    for i, sentence_data in enumerate(augmented_data):
        print(f"\nSentence {i+1}: {sentence_data['clause_text']}")
        print(f"  AI Category: {sentence_data['ai_category']}")
        print(f"  User Concern: {sentence_data['user_concern_level']}")
        if sentence_data['recommendations']:
            print("  Recommendations:")
            for rec in sentence_data['recommendations']:
                print(f"    - {rec['title']}: {rec['text']}")
        else:
            print("  No specific recommendations triggered.")
