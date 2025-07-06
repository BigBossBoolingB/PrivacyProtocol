# Main application orchestrator for Privacy Protocol
from .interpretation.interpreter import Interpreter
from .interpretation.clause_identifier import ClauseIdentifier
from .user_management.profiles import UserProfile
from .risk_assessment.scorer import RiskScorer
from .data_tracking.policy_tracker import PolicyTracker
from .data_tracking.metadata_logger import MetadataLogger
from .action_center.recommender import Recommender
from .action_center.opt_out_navigator import OptOutNavigator

# Import new data structures
from .policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis
from .consent import UserConsent
from .data_attribute import DataAttribute, SensitivityLevel, ObfuscationMethod


class PrivacyProtocolApp:
    def __init__(self):
        self.interpreter = Interpreter()
        self.clause_identifier = ClauseIdentifier()
        self.profiles = {}  # In-memory store for user profiles, user_id -> UserProfile
        self.risk_scorer = RiskScorer()
        self.policy_tracker = PolicyTracker()
        self.metadata_logger = MetadataLogger()
        self.recommender = Recommender()
        self.opt_out_navigator = OptOutNavigator()

        # Placeholder storage for new data structures
        self.policies = {}  # In-memory store for PrivacyPolicy objects, policy_id -> PrivacyPolicy
        self.consents = {}  # In-memory store for UserConsent objects, consent_id -> UserConsent
        self.data_attributes = {} # In-memory store for DataAttribute objects, attribute_id -> DataAttribute

        print("PrivacyProtocolApp initialized with core components and data structure placeholders.")

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

    # Example of creating and storing a PrivacyPolicy (conceptual)
    example_parsed_policy = PrivacyPolicy(
        version="1.0",
        data_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
        purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],
        retention_period="Until user deletes account",
        third_parties_shared_with=["Analytics Inc."],
        legal_basis=[LegalBasis.CONSENT, LegalBasis.CONTRACT],
        text_summary="This is a sample machine-readable policy summary."
    )
    app.policies[example_parsed_policy.policy_id] = example_parsed_policy
    print(f"\n--- Example Parsed Policy Stored ---")
    print(f"Stored policy with ID: {example_parsed_policy.policy_id}")
    print(f"Total policies in app store: {len(app.policies)}")

    # Example of creating and storing UserConsent (conceptual)
    example_consent = UserConsent(
        user_id=user1_id,
        policy_id=example_parsed_policy.policy_id,
        policy_version=example_parsed_policy.version,
        data_categories_consented=[DataCategory.PERSONAL_INFO],
        purposes_consented=[Purpose.SERVICE_DELIVERY]
    )
    app.consents[example_consent.consent_id] = example_consent
    print(f"\n--- Example User Consent Stored ---")
    print(f"Stored consent with ID: {example_consent.consent_id} for user {user1_id}")
    print(f"Total consents in app store: {len(app.consents)}")


if __name__ == "__main__":
    main()
