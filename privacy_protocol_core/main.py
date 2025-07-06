# Main application orchestrator for Privacy Protocol
from .interpretation.interpreter import Interpreter
from .interpretation.clause_identifier import ClauseIdentifier
from .user_management.profiles import UserProfile
from .risk_assessment.scorer import RiskScorer
from .data_tracking.policy_tracker import PolicyTracker
from .data_tracking.metadata_logger import MetadataLogger
from .action_center.recommender import Recommender
from .action_center.opt_out_navigator import OptOutNavigator

class PrivacyProtocolApp:
    def __init__(self):
        self.interpreter = Interpreter()
        self.clause_identifier = ClauseIdentifier()
        self.profiles = {} # In-memory store for user profiles, user_id -> UserProfile
        self.risk_scorer = RiskScorer()
        self.policy_tracker = PolicyTracker()
        self.metadata_logger = MetadataLogger()
        self.recommender = Recommender()
        self.opt_out_navigator = OptOutNavigator()
        print("PrivacyProtocolApp initialized.")

    def get_or_create_user_profile(self, user_id):
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(user_id)
        return self.profiles[user_id]

    def analyze_policy(self, user_id, policy_url, policy_text):
        """
        Analyzes a privacy policy for a given user.
        """
        print(f"Analyzing policy: {policy_url} for user: {user_id}")
        user_profile = self.get_or_create_user_profile(user_id)

        # Interpretation
        plain_language_summary = self.interpreter.translate_clause(policy_text[:500]) # Example: summarize first 500 chars
        disagreeable_clauses = self.clause_identifier.find_disagreement_clauses(policy_text)
        questionable_clauses = self.clause_identifier.find_questionable_clauses(policy_text)

        # Risk Assessment
        risk_score = self.risk_scorer.calculate_risk_score(policy_text, user_profile)

        # Recommendations
        recommendations = self.recommender.generate_recommendations(policy_text, risk_score, user_profile)

        # Logging
        self.metadata_logger.log_interaction(user_id, policy_url, "policy_analyzed", {"risk_score": risk_score})

        return {
            "plain_language_summary": plain_language_summary,
            "disagreeable_clauses": disagreeable_clauses,
            "questionable_clauses": questionable_clauses,
            "risk_score": risk_score,
            "recommendations": recommendations
        }

    # Add more methods to expose other functionalities

def main():
    app = PrivacyProtocolApp()

    # Example Usage
    user1_id = "user123"
    example_policy_url = "http://example.com/privacy"
    example_policy_text = """
    This is a privacy policy. We collect your data. We may share your data with third parties for marketing.
    We also engage in data selling. You agree to all terms.
    """

    user_profile = app.get_or_create_user_profile(user1_id)
    user_profile.set_tolerance("data_sharing", "low")

    analysis_result = app.analyze_policy(user1_id, example_policy_url, example_policy_text)

    print("\n--- Analysis Result ---")
    for key, value in analysis_result.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    opt_out_link = app.opt_out_navigator.get_opt_out_link("example_service.com")
    print(f"\nOpt-out link for example_service.com: {opt_out_link}")

    deletion_email = app.opt_out_navigator.get_data_deletion_template(
        "Example Service", "John Doe", "john.doe@example.com"
    )
    print(f"\nData Deletion Email Template:\n{deletion_email}")

if __name__ == "__main__":
    main()
