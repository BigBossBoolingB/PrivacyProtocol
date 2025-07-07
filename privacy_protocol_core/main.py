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

# Import new Stores
from .policy_store import PolicyStore
from .consent_store import ConsentStore

# Import PrivacyEnforcer and MockDataGenerator
from .privacy_enforcer import PrivacyEnforcer
from .demo_helpers.mock_data_generator import MockDataGenerator


class PrivacyProtocolApp:
    def __init__(self, base_storage_path="./_app_data"):
        self.base_storage_path = base_storage_path
        self.interpreter = Interpreter() # Remains for original policy text analysis
        self.clause_identifier = ClauseIdentifier() # Remains
        self.profiles = {}  # In-memory store for user profiles, user_id -> UserProfile
        self.risk_scorer = RiskScorer() # Remains
        self.policy_tracker = PolicyTracker()
        self.metadata_logger = MetadataLogger()
        self.recommender = Recommender()
        self.opt_out_navigator = OptOutNavigator()

        # Initialize stores
        self.policy_store = PolicyStore(base_path=f"{self.base_storage_path}/policies/")
        self.consent_store = ConsentStore(base_path=f"{self.base_storage_path}/consents/")

        # Initialize core components that depend on stores or each other
        self.consent_manager = ConsentManager(consent_store=self.consent_store)
        self.policy_evaluator = PolicyEvaluator()
        self.data_classifier = DataClassifier()
        self.obfuscation_engine = ObfuscationEngine()

        # Initialize PrivacyEnforcer with all its dependencies
        self.privacy_enforcer = PrivacyEnforcer(
            policy_store=self.policy_store,
            consent_manager=self.consent_manager,
            data_classifier=self.data_classifier,
            policy_evaluator=self.policy_evaluator,
            obfuscation_engine=self.obfuscation_engine
        )

        self.data_attributes_registry = self.data_classifier.attribute_registry
        self._policy_cache = {}

        print(f"PrivacyProtocolApp initialized with PrivacyEnforcer. Storage at: {self.base_storage_path}")

    def get_policy(self, policy_id: str, version: str = None) -> PrivacyPolicy | None:
        """Gets a policy, using cache and loading from store if necessary."""
        # Simplified: version=None means latest. PolicyStore handles loading latest.
        # More complex caching would involve specific version lookups.
        cache_key = (policy_id, version if version else "latest") # Crude key for latest

        if cache_key in self._policy_cache:
            return self._policy_cache[cache_key]

        policy = self.policy_store.load_policy(policy_id, version=version)
        if policy:
            # If we loaded latest, the actual version might be different than "latest" string
            # Re-key with actual version for more precise caching if version was None
            actual_cache_key = (policy.policy_id, policy.version)
            self._policy_cache[actual_cache_key] = policy
            if version is None: # If we asked for latest, also cache it under the "latest" key
                 self._policy_cache[cache_key] = policy
        return policy

    def save_policy(self, policy: PrivacyPolicy):
        """Saves a policy to the store and updates cache."""
        if self.policy_store.save_policy(policy):
            cache_key = (policy.policy_id, policy.version)
            self._policy_cache[cache_key] = policy
            # Invalidate or update "latest" cache entry for this policy_id
            latest_cache_key = (policy.policy_id, "latest")
            if latest_cache_key in self._policy_cache:
                # Re-fetch latest to update cache, or smarter logic
                del self._policy_cache[latest_cache_key]
                self.get_policy(policy.policy_id) # This will reload and cache latest
        else:
            print(f"Warning: Failed to save policy {policy.policy_id} v{policy.version} to store.")


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

    # --- Setup Policy and User for demonstrating persistence ---
    app_storage_path = "./_app_storage_main_demo" # Define a specific path for this demo
    # Clean up previous demo data if any - for fresh run
    import shutil
    try:
        shutil.rmtree(app_storage_path)
        print(f"Cleaned up old demo storage at {app_storage_path}")
    except FileNotFoundError:
        pass # No old data to clean

    app = PrivacyProtocolApp(base_storage_path=app_storage_path) # Use the specific path

    # Create and Save a PrivacyPolicy using PolicyStore via app method
    example_policy_id = "main_example_policy_1"
    example_policy_obj = PrivacyPolicy(
        policy_id=example_policy_id,
        version="1.0",
        data_categories=[
            DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.TECHNICAL_INFO
        ],
        purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS, Purpose.MARKETING], # Added MARKETING
        retention_period="Until user deletes account",
        third_parties_shared_with=["Analytics Inc.", "SomeAnalyticsTool"],
        legal_basis=[LegalBasis.CONSENT, LegalBasis.CONTRACT],
        text_summary="This is a sample machine-readable policy, now persisted."
    )
    app.save_policy(example_policy_obj)
    print(f"\n--- Example PrivacyPolicy Saved ---")
    print(f"Policy ID: {example_policy_obj.policy_id}, Version: {example_policy_obj.version} saved to store.")

    # Load the policy back to ensure it was saved
    loaded_policy = app.get_policy(example_policy_id, "1.0")
    assert loaded_policy is not None and loaded_policy.version == "1.0"
    print(f"Policy {loaded_policy.policy_id} v{loaded_policy.version} loaded successfully from store.")


    # Define some data attributes (can still be done as before, registry is part of classifier)
    email_attr_def = DataAttribute(attribute_name="email_address", category=DataCategory.PERSONAL_INFO,
                                   obfuscation_method_preferred=ObfuscationMethod.HASH)
    app.data_attributes_registry[email_attr_def.attribute_name] = email_attr_def

    ip_attr_def = DataAttribute(attribute_name="ip_address", category=DataCategory.TECHNICAL_INFO,
                                obfuscation_method_preferred=ObfuscationMethod.REDACT)
    app.data_attributes_registry[ip_attr_def.attribute_name] = ip_attr_def


    # User grants consent via ConsentManager (which now uses ConsentStore)
    print(f"\n--- User '{user1_id}' Granting Consent for Policy '{loaded_policy.policy_id}' ---")
    user1_consent_data = UserConsent(
        user_id=user1_id,
        policy_id=loaded_policy.policy_id,
        policy_version=loaded_policy.version,
        data_categories_consented=[DataCategory.PERSONAL_INFO],
        purposes_consented=[Purpose.SERVICE_DELIVERY],
        third_parties_consented=[]
    )
    app.consent_manager.add_consent(user1_consent_data)
    print(f"Consent ID {user1_consent_data.consent_id} added for user '{user1_id}'.")

    active_consent_user1 = app.consent_manager.get_active_consent(user_id=user1_id, policy_id=loaded_policy.policy_id)
    assert active_consent_user1 is not None
    print(f"Retrieved active consent for {user1_id}: Purposes: {[p.value for p in active_consent_user1.purposes_consented]}, Categories: {[dc.value for dc in active_consent_user1.data_categories_consented]}")


    # --- Data Classification and Obfuscation Examples (using loaded_policy) ---
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
        policy=loaded_policy, # Use loaded policy
        consent=active_consent_user1,
        proposed_purpose=Purpose.SERVICE_DELIVERY,
        data_classifier=app.data_classifier,
        policy_evaluator=app.policy_evaluator
    )
    print(f"Processed for SERVICE_DELIVERY (User1): {processed_data_service_delivery}")
    assert processed_data_service_delivery["email"] == "johndoe@example.com"
    assert processed_data_service_delivery["ip_address"] != "198.51.100.42"
    assert processed_data_service_delivery["last_page_visited"] != "/home"
    assert processed_data_service_delivery["user_id"] == "guid-xyz-123"


    # Scenario B: Process data for ANALYTICS (user1 has NOT consented to ANALYTICS)
    # All fields should be obfuscated as the purpose is not consented.
    # Policy itself allows ANALYTICS for PERSONAL_INFO, USAGE_DATA, TECHNICAL_INFO.

    processed_data_analytics_user1 = app.obfuscation_engine.process_data_for_operation(
        raw_data=sample_raw_data_user1,
        policy=loaded_policy, # Use loaded policy
        consent=active_consent_user1, # This consent doesn't allow ANALYTICS
        proposed_purpose=Purpose.ANALYTICS,
        data_classifier=app.data_classifier,
        policy_evaluator=app.policy_evaluator
    )
    print(f"Processed for ANALYTICS (User1 - no consent for this purpose): {processed_data_analytics_user1}")
    assert processed_data_analytics_user1["email"] != "johndoe@example.com"
    assert processed_data_analytics_user1["ip_address"] != "198.51.100.42"
    assert processed_data_analytics_user1["last_page_visited"] != "/home"
    assert processed_data_analytics_user1["user_id"] != "guid-xyz-123"


    # Scenario C: User2 - different consent (consents to ANALYTICS for USAGE_DATA and TECHNICAL_INFO)
    user2_id = "user456"
    user2_consent_data = UserConsent(
        user_id=user2_id, policy_id=loaded_policy.policy_id, policy_version=loaded_policy.version,
        data_categories_consented=[DataCategory.USAGE_DATA, DataCategory.TECHNICAL_INFO],
        purposes_consented=[Purpose.ANALYTICS],
        third_parties_consented=["SomeAnalyticsTool"]
    )
    app.consent_manager.add_consent(user2_consent_data)
    active_consent_user2 = app.consent_manager.get_active_consent(user_id=user2_id, policy_id=loaded_policy.policy_id)

    processed_data_analytics_user2 = app.obfuscation_engine.process_data_for_operation(
        raw_data=sample_raw_data_user1,
        policy=loaded_policy, # Use loaded policy
        consent=active_consent_user2,
        proposed_purpose=Purpose.ANALYTICS,
        data_classifier=app.data_classifier,
        policy_evaluator=app.policy_evaluator,
        proposed_third_party="SomeAnalyticsTool"
    )
    print(f"Processed for ANALYTICS (User2 - specific consent): {processed_data_analytics_user2}")
    assert processed_data_analytics_user2["email"] != "johndoe@example.com"
    assert processed_data_analytics_user2["ip_address"] == "198.51.100.42"
    assert processed_data_analytics_user2["last_page_visited"] == "/home"
    assert processed_data_analytics_user2["user_id"] != "guid-xyz-123"

    # --- Simulate App Restart ---
    print("\n--- Simulating App Restart ---")
    app_restarted = PrivacyProtocolApp(base_storage_path=app_storage_path)

    # Verify policy can be loaded
    reloaded_policy = app_restarted.get_policy(example_policy_id, "1.0")
    assert reloaded_policy is not None
    assert reloaded_policy.text_summary == "This is a sample machine-readable policy, now persisted."
    print(f"Policy '{reloaded_policy.policy_id}' v{reloaded_policy.version} reloaded successfully.")

    # Verify user1's consent can be loaded
    reloaded_consent_user1 = app_restarted.consent_manager.get_active_consent(user1_id, example_policy_id)
    assert reloaded_consent_user1 is not None
    assert reloaded_consent_user1.consent_id == user1_consent_data.consent_id
    print(f"Active consent for '{user1_id}' reloaded successfully.")

    # Verify user2's consent can be loaded
    reloaded_consent_user2 = app_restarted.consent_manager.get_active_consent(user2_id, example_policy_id)
    assert reloaded_consent_user2 is not None
    assert reloaded_consent_user2.consent_id == user2_consent_data.consent_id
    print(f"Active consent for '{user2_id}' reloaded successfully.")

    # Re-run an evaluation with reloaded components
    processed_data_restarted = app_restarted.obfuscation_engine.process_data_for_operation(
        raw_data=sample_raw_data_user1,
        policy=reloaded_policy,
        consent=reloaded_consent_user2, # Using user2's consent for ANALYTICS
        proposed_purpose=Purpose.ANALYTICS,
        data_classifier=app_restarted.data_classifier,
        policy_evaluator=app_restarted.policy_evaluator,
        proposed_third_party="SomeAnalyticsTool"
    )
    print(f"Processed for ANALYTICS (User2, after restart): {processed_data_restarted}")
    assert processed_data_restarted["ip_address"] == "198.51.100.42"
    assert processed_data_restarted["last_page_visited"] == "/home"

    # Clean up demo storage path after successful run
    try:
        shutil.rmtree(app_storage_path)
        print(f"Cleaned up demo storage at {app_storage_path} after successful run.")
    except FileNotFoundError:
        pass

    # --- PrivacyEnforcer Demonstration ---
    print("\n\n--- PrivacyEnforcer End-to-End Demonstration ---")
    # Re-initialize app for a clean enforcer demo with the same persisted data
    enforcer_app = PrivacyProtocolApp(base_storage_path=app_storage_path) # This will reload policy/consent

    mock_data_gen = MockDataGenerator()

    # User1 (user123) has consent for PERSONAL_INFO for SERVICE_DELIVERY
    # User2 (user456) has consent for USAGE_DATA, TECHNICAL_INFO for ANALYTICS with "SomeAnalyticsTool"

    print(f"\n--- Processing for User: {user1_id} ---")
    login_event_u1 = mock_data_gen.generate_user_login_event(user_id=user1_id)
    print(f"Original Login Event (User1): {login_event_u1}")

    processed_login_sd_u1, status_login_sd_u1 = enforcer_app.privacy_enforcer.process_data_record(
        user_id=user1_id, policy_id=example_policy_id, policy_version="1.0",
        data_record=login_event_u1, intended_purpose=Purpose.SERVICE_DELIVERY
    )
    print(f"Processed for SERVICE_DELIVERY (User1): {processed_login_sd_u1}, Status: {status_login_sd_u1}")
    # Expected: user_id raw, ip_address obfuscated (TECHNICAL_INFO not consented for SD by user1)
    assert processed_login_sd_u1['user_id'] == user1_id
    assert processed_login_sd_u1['ip_address'] != login_event_u1['ip_address']


    profile_update_u1 = mock_data_gen.generate_user_profile_data(user_id=user1_id, include_optional=False)
    profile_update_u1['email'] = "new.email.u1@example.com" # Ensure email key exists
    print(f"Original Profile Update (User1): {profile_update_u1}")
    processed_profile_marketing_u1, status_profile_marketing_u1 = enforcer_app.privacy_enforcer.process_data_record(
        user_id=user1_id, policy_id=example_policy_id, policy_version="1.0",
        data_record=profile_update_u1, intended_purpose=Purpose.MARKETING # User1 did not consent to MARKETING
    )
    print(f"Processed for MARKETING (User1): {processed_profile_marketing_u1}, Status: {status_profile_marketing_u1}")
    # Expected: all PII fields obfuscated as MARKETING purpose not consented by user1
    assert processed_profile_marketing_u1['email'] != profile_update_u1['email']
    assert processed_profile_marketing_u1['full_name'] != profile_update_u1['full_name']


    print(f"\n--- Processing for User: {user2_id} ---")
    page_view_u2 = mock_data_gen.generate_page_view_event(user_id=user2_id, page_url="/analytics_dashboard")
    print(f"Original Page View (User2): {page_view_u2}")
    processed_pv_analytics_u2, status_pv_analytics_u2 = enforcer_app.privacy_enforcer.process_data_record(
        user_id=user2_id, policy_id=example_policy_id, policy_version="1.0",
        data_record=page_view_u2, intended_purpose=Purpose.ANALYTICS, intended_third_party="SomeAnalyticsTool"
    )
    print(f"Processed for ANALYTICS with SomeAnalyticsTool (User2): {processed_pv_analytics_u2}, Status: {status_pv_analytics_u2}")
    # Expected: user_id (Other by default) obfuscated. page_url, referrer, ip_address (USAGE/TECHNICAL) raw.
    assert processed_pv_analytics_u2['user_id'] != user2_id # Classified as OTHER, not consented for ANALYTICS
    assert processed_pv_analytics_u2['page_url'] == page_view_u2['page_url']
    assert processed_pv_analytics_u2['ip_address'] == page_view_u2['ip_address']
    if page_view_u2.get('referrer'): # Referrer is optional
         assert processed_pv_analytics_u2['referrer'] == page_view_u2['referrer']


    sensor_data_u2 = mock_data_gen.generate_sensor_data(device_id=f"device_{user2_id}")
    sensor_data_u2['user_id_associated'] = user2_id # Add a PII field not typically in sensor data
    print(f"Original Sensor Data (User2): {sensor_data_u2}")
    processed_sensor_sd_u2, status_sensor_sd_u2 = enforcer_app.privacy_enforcer.process_data_record(
        user_id=user2_id, policy_id=example_policy_id, policy_version="1.0",
        data_record=sensor_data_u2, intended_purpose=Purpose.SERVICE_DELIVERY # User2 did not consent any category for SD
    )
    print(f"Processed for SERVICE_DELIVERY (User2): {processed_sensor_sd_u2}, Status: {status_sensor_sd_u2}")
    # Expected: All fields obfuscated as User2 has no consent for SERVICE_DELIVERY
    assert processed_sensor_sd_u2['device_id'] != sensor_data_u2['device_id']
    assert processed_sensor_sd_u2['latitude'] != sensor_data_u2['latitude']
    assert processed_sensor_sd_u2['user_id_associated'] != sensor_data_u2['user_id_associated']

    # Final cleanup of demo storage
    try:
        shutil.rmtree(app_storage_path)
        print(f"\nFinal cleanup of demo storage at {app_storage_path} successful.")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"\nError during final cleanup of demo storage: {e}")


if __name__ == "__main__":
    main()
