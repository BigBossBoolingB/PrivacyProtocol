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

# Import new manager and evaluator
from .consent_manager import ConsentManager
from .policy_evaluator import PolicyEvaluator


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

        # Initialize new managers and evaluators
        self.consent_manager = ConsentManager()
        self.policy_evaluator = PolicyEvaluator()

        # Placeholder storage for policies and attributes (consents managed by ConsentManager)
        self.policies = {}  # In-memory store for PrivacyPolicy objects, policy_id -> PrivacyPolicy
        self.data_attributes_registry = {} # In-memory store for DataAttribute objects, attribute_id -> DataAttribute

        print("PrivacyProtocolApp initialized with ConsentManager and PolicyEvaluator.")

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
    print(f"\n--- Example PrivacyPolicy Created ---")
    print(f"Policy ID: {example_parsed_policy.policy_id}, Version: {example_parsed_policy.version}")

    # Define some data attributes that might be used
    email_attribute = DataAttribute(attribute_name="user_email", category=DataCategory.PERSONAL_INFO)
    app.data_attributes_registry[email_attribute.attribute_id] = email_attribute

    usage_attribute = DataAttribute(attribute_name="page_views", category=DataCategory.USAGE_DATA)
    app.data_attributes_registry[usage_attribute.attribute_id] = usage_attribute


    # User grants consent via ConsentManager
    print(f"\n--- User '{user1_id}' Granting Consent ---")
    user1_consent_to_policy = UserConsent(
        user_id=user1_id,
        policy_id=example_parsed_policy.policy_id,
        policy_version=example_parsed_policy.version,
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA], # Consents to both
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS],      # Consents to Service Delivery & Analytics
        third_parties_consented=["Analytics Inc."]                             # Consents to one third party
    )
    app.consent_manager.add_consent(user1_consent_to_policy)
    print(f"Consent ID {user1_consent_to_policy.consent_id} added for user '{user1_id}' for policy '{example_parsed_policy.policy_id}'.")
    retrieved_consent = app.consent_manager.get_active_consent(user_id=user1_id, policy_id=example_parsed_policy.policy_id)
    if retrieved_consent:
        print(f"Retrieved active consent: version {retrieved_consent.policy_version}, purposes: {[p.value for p in retrieved_consent.purposes_consented]}")


    # --- Policy Evaluation Examples ---
    print("\n--- Policy Evaluation Examples ---")

    # Scenario 1: Use email for Service Delivery (should be permitted)
    attributes_for_op1 = [email_attribute]
    purpose_op1 = Purpose.SERVICE_DELIVERY
    is_permitted1 = app.policy_evaluator.is_operation_permitted(
        policy=example_parsed_policy,
        consent=retrieved_consent,
        data_attributes=attributes_for_op1,
        proposed_purpose=purpose_op1
    )
    print(f"Operation: Use '{email_attribute.attribute_name}' for '{purpose_op1.value}'. Permitted: {is_permitted1}")
    assert is_permitted1 == True

    # Scenario 2: Use email for Marketing (user did not consent to Marketing purpose)
    purpose_op2 = Purpose.MARKETING # Policy allows Marketing, but user consent doesn't
    is_permitted2 = app.policy_evaluator.is_operation_permitted(
        policy=example_parsed_policy, # Policy allows marketing
        consent=retrieved_consent,    # Consent does not have marketing
        data_attributes=attributes_for_op1, # email
        proposed_purpose=purpose_op2
    )
    print(f"Operation: Use '{email_attribute.attribute_name}' for '{purpose_op2.value}'. Permitted: {is_permitted2}")
    assert is_permitted2 == False # example_parsed_policy doesn't list MARKETING, this should be false from policy check.
                                  # Let's assume policy *did* list marketing for a better consent test.
                                  # Correcting example_parsed_policy to include MARKETING for this test.
    example_parsed_policy.purposes.append(Purpose.MARKETING) # Temporarily add for this test case.
    is_permitted2_policy_allows = app.policy_evaluator.is_operation_permitted(
        policy=example_parsed_policy,
        consent=retrieved_consent, # User consent still doesn't have MARKETING
        data_attributes=attributes_for_op1,
        proposed_purpose=purpose_op2
    )
    print(f"Operation (policy updated): Use '{email_attribute.attribute_name}' for '{purpose_op2.value}'. Permitted: {is_permitted2_policy_allows}")
    assert is_permitted2_policy_allows == False # Still false due to consent

    # Scenario 3: Use usage_data for Analytics with "Analytics Inc." (should be permitted)
    attributes_for_op3 = [usage_attribute]
    purpose_op3 = Purpose.ANALYTICS
    third_party_op3 = "Analytics Inc."
    is_permitted3 = app.policy_evaluator.is_operation_permitted(
        policy=example_parsed_policy,
        consent=retrieved_consent,
        data_attributes=attributes_for_op3,
        proposed_purpose=purpose_op3,
        proposed_third_party=third_party_op3
    )
    print(f"Operation: Use '{usage_attribute.attribute_name}' for '{purpose_op3.value}' with '{third_party_op3}'. Permitted: {is_permitted3}")
    assert is_permitted3 == True

    # Scenario 4: Use email for Analytics with "OtherCompany" (third party not consented)
    third_party_op4 = "OtherCompany"
    is_permitted4 = app.policy_evaluator.is_operation_permitted(
        policy=example_parsed_policy,
        consent=retrieved_consent,
        data_attributes=attributes_for_op1, # email
        proposed_purpose=purpose_op3,       # Analytics
        proposed_third_party=third_party_op4
    )
    print(f"Operation: Use '{email_attribute.attribute_name}' for '{purpose_op3.value}' with '{third_party_op4}'. Permitted: {is_permitted4}")
    assert is_permitted4 == False

    # Scenario 5: User revokes consent, then try an operation
    print(f"\n--- User '{user1_id}' Revoking Consent ---")
    app.consent_manager.revoke_consent(user_id=user1_id, policy_id=example_parsed_policy.policy_id)
    print(f"Consent for policy '{example_parsed_policy.policy_id}' for user '{user1_id}' revoked.")
    revoked_consent_check = app.consent_manager.get_active_consent(user_id=user1_id, policy_id=example_parsed_policy.policy_id)
    is_permitted5 = app.policy_evaluator.is_operation_permitted(
        policy=example_parsed_policy,
        consent=revoked_consent_check, # Should be None or inactive
        data_attributes=attributes_for_op1,
        proposed_purpose=purpose_op1
    )
    print(f"Operation after revocation: Use '{email_attribute.attribute_name}' for '{purpose_op1.value}'. Permitted: {is_permitted5}")
    assert is_permitted5 == False


if __name__ == "__main__":
    main()
