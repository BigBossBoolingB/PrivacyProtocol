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

# Import new DataClassifier and ObfuscationEngine
from .data_classifier import DataClassifier
from .obfuscation_engine import ObfuscationEngine


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
        self.consent_manager = ConsentManager()
        self.policy_evaluator = PolicyEvaluator()

        # Initialize DataClassifier and ObfuscationEngine
        self.data_classifier = DataClassifier() # Can be initialized with a registry if needed
        self.obfuscation_engine = ObfuscationEngine()

        # Placeholder storage for policies and attributes (consents managed by ConsentManager)
        self.policies = {}  # In-memory store for PrivacyPolicy objects, policy_id -> PrivacyPolicy
        # data_attributes_registry can be part of DataClassifier or a separate registry managed by the app
        # For now, DataClassifier manages its own rules, but app might hold a central registry of known attributes.
        self.data_attributes_registry = self.data_classifier.attribute_registry

        print("PrivacyProtocolApp initialized with all components including Classifier and Obfuscator.")

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
        policy_id="main_example_policy_1", # Explicit ID for clarity
        version="1.0",
        data_categories=[
            DataCategory.PERSONAL_INFO,
            DataCategory.USAGE_DATA,
            DataCategory.TECHNICAL_INFO # Added for ip_address scenario
        ],
        purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS], # Marketing added later for a test
        retention_period="Until user deletes account",
        third_parties_shared_with=["Analytics Inc.", "SomeAnalyticsTool"], # Added SomeAnalyticsTool
        legal_basis=[LegalBasis.CONSENT, LegalBasis.CONTRACT],
        text_summary="This is a sample machine-readable policy summary."
    )
    app.policies[example_parsed_policy.policy_id] = example_parsed_policy
    print(f"\n--- Example PrivacyPolicy Created ---")
    print(f"Policy ID: {example_parsed_policy.policy_id}, Version: {example_parsed_policy.version}")

    # Define some data attributes that might be used - these are now classified on the fly mostly
    # but we can pre-register some for specific obfuscation methods if DataClassifier doesn't set them.
    email_attr_def = DataAttribute(attribute_name="email_address", category=DataCategory.PERSONAL_INFO,
                                   obfuscation_method_preferred=ObfuscationMethod.HASH)
    app.data_attributes_registry[email_attr_def.attribute_name] = email_attr_def

    ip_attr_def = DataAttribute(attribute_name="ip_address", category=DataCategory.TECHNICAL_INFO,
                                obfuscation_method_preferred=ObfuscationMethod.REDACT)
    app.data_attributes_registry[ip_attr_def.attribute_name] = ip_attr_def


    # User grants consent via ConsentManager
    print(f"\n--- User '{user1_id}' Granting Consent for Policy '{example_parsed_policy.policy_id}' ---")
    user1_consent_data = UserConsent(
        user_id=user1_id,
        policy_id=example_parsed_policy.policy_id,
        policy_version=example_parsed_policy.version,
        data_categories_consented=[DataCategory.PERSONAL_INFO], # Only consents to PERSONAL_INFO
        purposes_consented=[Purpose.SERVICE_DELIVERY],      # Only for Service Delivery
        third_parties_consented=[]                             # No third-party sharing consented
    )
    app.consent_manager.add_consent(user1_consent_data)
    active_consent_user1 = app.consent_manager.get_active_consent(user_id=user1_id, policy_id=example_parsed_policy.policy_id)
    if active_consent_user1:
        print(f"Active consent for {user1_id}: Purposes: {[p.value for p in active_consent_user1.purposes_consented]}, Categories: {[dc.value for dc in active_consent_user1.data_categories_consented]}")


    # --- Data Classification and Obfuscation Examples ---
    print("\n--- Data Classification and Obfuscation Examples ---")

    sample_raw_data_user1 = {
        "email": "johndoe@example.com",
        "ip_address": "198.51.100.42",
        "last_page_visited": "/home",
        "user_id": "guid-xyz-123"  # Changed from user_id_internal to match classifier rule
    }
    print(f"Original User Data: {sample_raw_data_user1}")

    # Scenario A: Process data for SERVICE_DELIVERY
    # For user1, SERVICE_DELIVERY is consented for PERSONAL_INFO only.
    # email (PERSONAL_INFO) -> raw
    # ip_address (TECHNICAL_INFO) -> obfuscated
    # last_page_visited (USAGE_DATA by rule) -> obfuscated
    # user_id (PERSONAL_INFO by rule) -> raw

    processed_data_service_delivery = app.obfuscation_engine.process_data_for_operation(
        raw_data=sample_raw_data_user1,
        policy=example_parsed_policy,
        consent=active_consent_user1,
        proposed_purpose=Purpose.SERVICE_DELIVERY,
        data_classifier=app.data_classifier,
        policy_evaluator=app.policy_evaluator
    )
    print(f"Processed for SERVICE_DELIVERY (User1): {processed_data_service_delivery}")
    assert processed_data_service_delivery["email"] == "johndoe@example.com"
    assert processed_data_service_delivery["ip_address"] != "198.51.100.42" # Should be redacted
    assert processed_data_service_delivery["last_page_visited"] != "/home"   # Should be obfuscated
    assert processed_data_service_delivery["user_id"] == "guid-xyz-123" # PERSONAL_INFO consented for SD


    # Scenario B: Process data for ANALYTICS (user1 has NOT consented to ANALYTICS)
    # All fields should be obfuscated as the purpose is not consented.
    # Policy itself allows ANALYTICS for PERSONAL_INFO, USAGE_DATA.
    example_parsed_policy.purposes.append(Purpose.ANALYTICS) # Ensure policy allows it

    processed_data_analytics_user1 = app.obfuscation_engine.process_data_for_operation(
        raw_data=sample_raw_data_user1,
        policy=example_parsed_policy,
        consent=active_consent_user1, # This consent doesn't allow ANALYTICS
        proposed_purpose=Purpose.ANALYTICS,
        data_classifier=app.data_classifier,
        policy_evaluator=app.policy_evaluator
    )
    print(f"Processed for ANALYTICS (User1 - no consent for this purpose): {processed_data_analytics_user1}")
    assert processed_data_analytics_user1["email"] != "johndoe@example.com"     # Obfuscated (hashed by pre-reg)
    assert processed_data_analytics_user1["ip_address"] != "198.51.100.42" # Obfuscated (redacted by pre-reg)
    assert processed_data_analytics_user1["last_page_visited"] != "/home"       # Obfuscated
    assert processed_data_analytics_user1["user_id"] != "guid-xyz-123" # Obfuscated


    # Scenario C: User2 - different consent (consents to ANALYTICS for USAGE_DATA and TECHNICAL_INFO)
    user2_id = "user456"
    user2_consent_data = UserConsent(
        user_id=user2_id, policy_id=example_parsed_policy.policy_id, policy_version=example_parsed_policy.version,
        data_categories_consented=[DataCategory.USAGE_DATA, DataCategory.TECHNICAL_INFO],
        purposes_consented=[Purpose.ANALYTICS],
        third_parties_consented=["SomeAnalyticsTool"]
    )
    app.consent_manager.add_consent(user2_consent_data)
    active_consent_user2 = app.consent_manager.get_active_consent(user_id=user2_id, policy_id=example_parsed_policy.policy_id)

    processed_data_analytics_user2 = app.obfuscation_engine.process_data_for_operation(
        raw_data=sample_raw_data_user1, # Same raw data
        policy=example_parsed_policy,
        consent=active_consent_user2,   # User2's consent
        proposed_purpose=Purpose.ANALYTICS,
        data_classifier=app.data_classifier,
        policy_evaluator=app.policy_evaluator,
        proposed_third_party="SomeAnalyticsTool"
    )
    print(f"Processed for ANALYTICS (User2 - specific consent): {processed_data_analytics_user2}")
    assert processed_data_analytics_user2["email"] != "johndoe@example.com" # PERSONAL_INFO not consented by User2 for ANALYTICS
    assert processed_data_analytics_user2["ip_address"] == "198.51.100.42"   # TECHNICAL_INFO consented for ANALYTICS
    assert processed_data_analytics_user2["last_page_visited"] == "/home"    # USAGE_DATA consented for ANALYTICS
    assert processed_data_analytics_user2["user_id"] != "guid-xyz-123" # PERSONAL_INFO not consented


if __name__ == "__main__":
    main()
