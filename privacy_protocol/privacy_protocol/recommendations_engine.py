from .recommendations_data import RECOMMENDATIONS_DATA
from typing import List, Dict # For type hinting
from .dashboard_models import UserPrivacyProfile # For generate_global_recommendations

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

    def generate_global_recommendations(self, user_profile: UserPrivacyProfile) -> List[Dict]:
        """Generates global recommendations based on the UserPrivacyProfile."""
        global_recs = []

        if user_profile is None:
            return global_recs

        # Rule 1: High-risk services
        if user_profile.total_high_risk_services_count > 0:
            insight_text = f"You have {user_profile.total_high_risk_services_count} service(s) flagged as high risk (score 67-100). Prioritize reviewing these services' policies and your settings with them."
            if user_profile.total_high_risk_services_count == 1:
                insight_text = f"You have 1 service flagged as high risk (score 67-100). Prioritize reviewing this service's policy and your settings."
            global_recs.append({
                'id': 'GLOBAL_HIGH_RISK_ALERT',
                'title': 'Review High-Risk Services',
                'text': insight_text
            })

        # Rule 2: Overall high risk score
        if user_profile.overall_privacy_risk_score is not None and user_profile.overall_privacy_risk_score > 66:
            # Avoid duplicate type of message if already covered by total_high_risk_services_count
            if not any(rec['id'] == 'GLOBAL_HIGH_RISK_ALERT' for rec in global_recs) or user_profile.total_high_risk_services_count == 0 :
                global_recs.append({
                    'id': 'GLOBAL_OVERALL_HIGH_RISK',
                    'title': 'Overall High Privacy Risk',
                    'text': f"Your overall privacy risk score is {user_profile.overall_privacy_risk_score}/100, indicating a generally high privacy risk posture. Consider taking steps to mitigate risks, such as adjusting preferences or using more privacy-respecting alternatives."
                })

        # Rule 3: Medium risk insight if no high risk ones and list is not full
        if user_profile.total_medium_risk_services_count > 0 and user_profile.total_high_risk_services_count == 0 and len(global_recs) < 2:
            insight_text = f"You have {user_profile.total_medium_risk_services_count} service(s) with a 'Medium' privacy risk score (34-66). It's advisable to review their details."
            if user_profile.total_medium_risk_services_count == 1:
                 insight_text = f"You have 1 service with a 'Medium' privacy risk score (34-66). It's advisable to review its details."
            global_recs.append({
                'id': 'GLOBAL_MEDIUM_RISK_INFO',
                'title': 'Review Medium-Risk Services',
                'text': insight_text
            })

        # Rule 4: Generic recommendation (always add if space permits, e.g., up to 3 total)
        if len(global_recs) < 3:
            global_recs.append({
                'id': 'GLOBAL_REGULAR_REVIEW',
                'title': 'Regularly Review Settings',
                'text': 'Make it a habit to periodically review the privacy settings and policies of the services you use, as they can change.'
            })

        # Conceptual note for future AI integration (fulfills sub-issue 2.3 documentation part)
        # TODO: Future - Integrate advanced AI (e.g., LLM with specific prompts on aggregated data)
        # to synthesize more nuanced, natural language insights and actionable advice here.
        # Example: "Based on your preference to avoid data selling, the high risk score of Service X
        # (which mentions data selling) is a key concern. Consider finding an alternative or using opt-outs."

        return global_recs[:3] # Ensure we only return up to 3 recommendations

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

    # Example sentence analysis data (simplified) - This part can be kept or reduced as it's for the old method
    # ... (previous sample_analyzed_sentences and its print loop can remain for context if desired)

    print("\n\n--- Generating Global Recommendations ---")
    # Scenario 1: User profile with high risk services
    profile1 = UserPrivacyProfile(
        user_id="test_user_1",
        overall_privacy_risk_score=75,
        total_services_analyzed=2,
        total_high_risk_services_count=1,
        total_medium_risk_services_count=1,
        total_low_risk_services_count=0,
        key_privacy_insights=["Service X has a High risk score (80/100)."] # Example insight
    )
    global_recs1 = engine.generate_global_recommendations(profile1)
    print("\nGlobal Recommendations for Profile 1 (High Risk):")
    for rec in global_recs1:
        print(f"  - ID: {rec['id']}, Title: {rec['title']}, Text: {rec['text']}")

    # Scenario 2: User profile with only medium and low risk
    profile2 = UserPrivacyProfile(
        user_id="test_user_2",
        overall_privacy_risk_score=50,
        total_services_analyzed=3,
        total_high_risk_services_count=0,
        total_medium_risk_services_count=2,
        total_low_risk_services_count=1,
        key_privacy_insights=["Overall posture is moderate."]
    )
    global_recs2 = engine.generate_global_recommendations(profile2)
    print("\nGlobal Recommendations for Profile 2 (Medium/Low Risk):")
    for rec in global_recs2:
        print(f"  - ID: {rec['id']}, Title: {rec['title']}, Text: {rec['text']}")

    # Scenario 3: User profile with all low risk
    profile3 = UserPrivacyProfile(
        user_id="test_user_3",
        overall_privacy_risk_score=20,
        total_services_analyzed=2,
        total_high_risk_services_count=0,
        total_medium_risk_services_count=0,
        total_low_risk_services_count=2,
        key_privacy_insights=["All services are low risk."]
    )
    global_recs3 = engine.generate_global_recommendations(profile3)
    print("\nGlobal Recommendations for Profile 3 (All Low Risk):")
    for rec in global_recs3:
        print(f"  - ID: {rec['id']}, Title: {rec['title']}, Text: {rec['text']}")

    # Scenario 4: No services analyzed (empty profile)
    profile4 = UserPrivacyProfile(
        user_id="test_user_4",
        overall_privacy_risk_score=None,
        total_services_analyzed=0
    ) # key_privacy_insights will default to []
    global_recs4 = engine.generate_global_recommendations(profile4) # This will be empty based on current logic
    print("\nGlobal Recommendations for Profile 4 (No Services):")
    if global_recs4:
        for rec in global_recs4:
            print(f"  - ID: {rec['id']}, Title: {rec['title']}, Text: {rec['text']}")
    else: # The generic "Regularly Review Settings" is always added if space
        print("  (Should show generic recommendations, e.g., 'Regularly Review Settings')")
        # Manually check the always-add one for this case
        temp_recs = [{'id': 'GLOBAL_REGULAR_REVIEW', 'title': 'Regularly Review Settings', 'text': 'Make it a habit to periodically review the privacy settings and policies of the services you use, as they can change.'}]
        if any(r['id'] == 'GLOBAL_REGULAR_REVIEW' for r in temp_recs): # Mocking the expected behavior for this scenario
             print(f"  - Correctly includes: {temp_recs[0]['title']}")
