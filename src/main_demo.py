# src/main_demo.py
"""
Demonstration script for the Privacy Protocol's core functionalities.
"""
import time
import os
import shutil # For cleaning up profile storage for demo consistency

# Assuming the script is run from the project root or 'src' is in PYTHONPATH
try:
    from privacy_framework.policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis
    from privacy_framework.consent import UserConsent
    from privacy_framework.data_attribute import DataAttribute, SensitivityLevel
    from privacy_interpreter import PrivacyInterpreter
    from privacy_profile_manager import PrivacyProfileManager, PrivacyProfile
    from privacy_framework.consent_manager import ConsentManager
    from privacy_framework.policy_evaluator import PolicyEvaluator
except ImportError:
    print("ImportError: Make sure you are running this script from the project root,")
    print("or that the 'src' directory is in your PYTHONPATH.")
    print("Example: python src/main_demo.py")
    exit(1)

def run_demonstration():
    """Runs the Privacy Protocol demonstration."""

    print("=======================================")
    print("Privacy Protocol Demonstration")
    print("=======================================\n")

    # --- 0. Configuration & Cleanup ---
    USER_ID = "demo_user_001"
    PROFILE_STORAGE_PATH = "user_profiles_demo/" # Specific path for demo

    # Clean up profile storage from previous demo runs for consistency
    if os.path.exists(PROFILE_STORAGE_PATH):
        shutil.rmtree(PROFILE_STORAGE_PATH)

    # --- 1. Initialize Core Components ---
    print("--- 1. Initializing Core Components ---")
    try:
        interpreter = PrivacyInterpreter() # Uses default 'en_core_web_sm'
        if not interpreter.nlp:
            print("ERROR: spaCy model for PrivacyInterpreter could not be loaded. Demo cannot proceed.")
            return
    except Exception as e:
        print(f"ERROR: Failed to initialize PrivacyInterpreter: {e}. Demo cannot proceed.")
        return

    profile_manager = PrivacyProfileManager(storage_path=PROFILE_STORAGE_PATH)
    consent_manager = ConsentManager()
    policy_evaluator = PolicyEvaluator()
    print("Components initialized.\n")

    # --- 2. Define & "Interpret" a Sample Privacy Policy ---
    print("--- 2. Defining & Interpreting a Sample Privacy Policy ---")
    sample_policy_text = """
    Our service collects your Personal Information like name and email for Service Delivery and Marketing.
    We also track Usage Data and Device Information (like IP address) for Analytics and to improve our services.
    We may share Usage Data with trusted analytics partners. Data is kept for 1 year.
    By using our service, you agree to this.
    """
    print(f"Sample Policy Text:\n{sample_policy_text[:150]}...\n")

    # Conceptual interpretation (V1 interpreter is basic)
    # In a full system, interpreter would output a structured PrivacyPolicy object.
    # Here, we use its V1 extraction and then manually construct the policy object for the demo.
    interpreted_keywords = interpreter.interpret_policy(sample_policy_text)
    print(f"Interpreter (V1) extracted keywords (example):")
    print(f"  Data Categories detected: {[dc.name for dc in interpreted_keywords.get('data_categories', [])]}")
    print(f"  Purposes detected: {[p.name for p in interpreted_keywords.get('purposes', [])]}\n")

    # Manually construct the PrivacyPolicy object based on the text for this demo
    demo_policy = PrivacyPolicy(
        policy_id="demo_policy_001",
        version=1,
        data_categories=[
            DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.DEVICE_INFO
        ],
        purposes=[
            Purpose.SERVICE_DELIVERY, Purpose.MARKETING, Purpose.ANALYTICS, Purpose.IMPROVEMENT
        ],
        retention_period="1 year",
        third_parties_shared_with=["trusted_analytics_partner_co"], # From policy text
        legal_basis=LegalBasis.CONSENT, # "By using our service, you agree" implies consent basis
        text_summary="Service collects PI, Usage, Device data for SD, Marketing, Analytics, Improvement. Shares with analytics partners."
    )
    print(f"Manually constructed PrivacyPolicy object (ID: {demo_policy.policy_id}) based on interpretation.\n")

    # --- 3. Create a User Privacy Profile ---
    print("--- 3. Creating a User Privacy Profile ---")
    profile_id = "user_default_profile"
    profile_name = "User's Default Settings"
    try:
        user_profile = profile_manager.create_profile(
            user_id=USER_ID,
            profile_id=profile_id,
            profile_name=profile_name,
            permitted_data_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
            permitted_purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS], # User is okay with SD and Analytics
            trusted_third_parties=["trusted_analytics_partner_co"], # User trusts this partner
            strictness_level=7
        )
        print(f"Created profile: '{user_profile.profile_name}' (ID: {user_profile.profile_id})")
        print(f"  Permitted Categories by profile: {[dc.name for dc in user_profile.permitted_data_categories]}")
        print(f"  Permitted Purposes by profile: {[p.name for p in user_profile.permitted_purposes]}\n")
    except ValueError as e:
        print(f"Error creating profile (already exists?): {e}")
        user_profile = profile_manager.load_profile(profile_id) # Try to load if it was from a partial previous run
        if not user_profile:
            print("Could not load existing profile. Demo might not work as expected.")
            return


    # --- 4. Grant User Consent (Derived from Profile or Explicit) ---
    print("--- 4. Granting User Consent for the Demo Policy ---")
    # For this demo, let's create a UserConsent object based on the user's profile
    # and the specific policy they are interacting with.
    # A real UI would present the policy and allow user to tweak choices from their profile.

    # User reviews `demo_policy` and decides.
    # Let's say user accepts categories/purposes from their profile that are ALSO in the policy.
    consented_categories = [
        cat for cat in user_profile.permitted_data_categories
        if cat in demo_policy.data_categories
    ]
    consented_purposes = [
        purp for purp in user_profile.permitted_purposes
        if purp in demo_policy.purposes
    ]
    # User explicitly DENIES marketing for this specific policy, even if profile might be more lenient elsewhere.
    if Purpose.MARKETING in consented_purposes: # Example of specific override
        consented_purposes.remove(Purpose.MARKETING)

    consented_third_parties = [
        tp for tp in user_profile.trusted_third_parties
        if tp in demo_policy.third_parties_shared_with
    ]

    user_consent_for_demo_policy = UserConsent(
        consent_id=f"consent_{USER_ID}_{demo_policy.policy_id}_{int(time.time())}",
        user_id=USER_ID,
        policy_id=demo_policy.policy_id,
        version=demo_policy.version,
        data_categories_consented=consented_categories,
        purposes_consented=consented_purposes,
        third_parties_consented=consented_third_parties,
        is_active=True
    )
    consent_manager.store_consent(user_consent_for_demo_policy)
    print(f"UserConsent (ID: {user_consent_for_demo_policy.consent_id}) created and stored:")
    print(f"  Consented Categories: {[dc.name for dc in user_consent_for_demo_policy.data_categories_consented]}")
    print(f"  Consented Purposes: {[p.name for p in user_consent_for_demo_policy.purposes_consented]}")
    print(f"  Consented Third Parties: {user_consent_for_demo_policy.third_parties_consented}\n")

    # --- 5. Evaluate Hypothetical Data Operations ---
    print("--- 5. Evaluating Hypothetical Data Operations ---")

    # Define some data attributes for operations
    email_attribute = DataAttribute("email", DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, is_pii=True)
    ip_address_attribute = DataAttribute("ip_address", DataCategory.DEVICE_INFO, SensitivityLevel.MEDIUM)
    browsing_history_attribute = DataAttribute("browsing_history", DataCategory.USAGE_DATA, SensitivityLevel.HIGH)

    operations_to_test = [
        {
            "description": "Send a welcome email (Service Delivery using Personal Info)",
            "attributes": [email_attribute],
            "purpose": Purpose.SERVICE_DELIVERY,
            "third_party": None,
            "expected": True # Profile allows PI for SD, Policy allows PI for SD
        },
        {
            "description": "Use email for Marketing purposes",
            "attributes": [email_attribute],
            "purpose": Purpose.MARKETING,
            "third_party": None,
            "expected": False # User explicitly denied MARKETING for this policy in step 4
        },
        {
            "description": "Collect IP address for Analytics",
            "attributes": [ip_address_attribute],
            "purpose": Purpose.ANALYTICS,
            "third_party": None,
            "expected": True # Profile allows USAGE/DEVICE for Analytics, Policy allows DEVICE for Analytics
                            # Note: User profile had USAGE_DATA for ANALYTICS, consent has USAGE_DATA.
                            # Policy has DEVICE_INFO for ANALYTICS.
                            # Consent has USAGE_DATA. IP address is DEVICE_INFO.
                            # This will depend on whether user_consent_for_demo_policy included DEVICE_INFO
                            # Based on current logic: consented_categories = [PERSONAL_INFO, USAGE_DATA]
                            # So this should be FALSE as DEVICE_INFO not in consented_categories.
                            # Let's adjust expected for this:
                            # Expected: False
        },
        {
            "description": "Share browsing history with 'trusted_analytics_partner_co' for Analytics",
            "attributes": [browsing_history_attribute], # USAGE_DATA
            "purpose": Purpose.ANALYTICS,
            "third_party": "trusted_analytics_partner_co",
            "expected": True # Profile allows USAGE for Analytics & trusts partner. Policy allows USAGE for Analytics & lists partner.
        },
        {
            "description": "Share email with 'unknown_partner.com' for Marketing",
            "attributes": [email_attribute],
            "purpose": Purpose.MARKETING,
            "third_party": "unknown_partner.com",
            "expected": False # Marketing denied by consent, and partner unknown/not consented.
        },
        {
            "description": "Use IP address for Research (purpose not in policy)",
            "attributes": [ip_address_attribute],
            "purpose": Purpose.RESEARCH,
            "third_party": None,
            "expected": False # RESEARCH not in demo_policy.purposes
        }
    ]

    # Adjusting expectation for operation 3 based on current consent derivation:
    # User profile has: permitted_data_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA]
    # Demo policy has: data_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.DEVICE_INFO]
    # Consented categories becomes intersection: [DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA]
    # IP address is DEVICE_INFO. So it's not in consented_categories.
    operations_to_test[2]["expected"] = False # "Collect IP address for Analytics"

    active_consent = consent_manager.get_active_consent(USER_ID, demo_policy.policy_id)
    if not active_consent:
        print("ERROR: Could not retrieve active consent for evaluation. Demo cannot continue accurately.")
        return

    for op in operations_to_test:
        print(f"\nEvaluating: {op['description']}")
        is_permitted = policy_evaluator.is_operation_permitted(
            policy=demo_policy,
            consent=active_consent, # Use the specific consent granted for this policy
            data_attributes_involved=op["attributes"],
            proposed_purpose=op["purpose"],
            proposed_third_party=op["third_party"]
        )
        result_str = "Permitted" if is_permitted else "Denied"
        expected_str = "Permitted" if op["expected"] else "Denied"
        status = "PASS" if is_permitted == op["expected"] else "FAIL"

        print(f"  Outcome: {result_str} (Expected: {expected_str}) - {status}")
        if not is_permitted:
             # Basic explanation (could be more detailed by inspecting evaluator's internal logic if exposed)
            if op["purpose"] not in demo_policy.purposes:
                print(f"  Reason hint: Purpose '{op['purpose'].name}' not allowed by policy.")
            elif active_consent:
                if op["purpose"] not in active_consent.purposes_consented:
                     print(f"  Reason hint: Purpose '{op['purpose'].name}' not in user's consent for this policy.")
                for attr in op["attributes"]:
                    if attr.category not in active_consent.data_categories_consented:
                        print(f"  Reason hint: Data category '{attr.category.name}' for attribute '{attr.attribute_name}' not in user's consent.")
                        break
                if op["third_party"] and (not active_consent.third_parties_consented or op["third_party"] not in active_consent.third_parties_consented) :
                     print(f"  Reason hint: Third party '{op['third_party']}' not in user's consent list for this policy.")


    print("\n--- 6. Demonstration Complete ---")
    print(f"User profiles for this demo are stored in: {os.path.abspath(PROFILE_STORAGE_PATH)}")
    print("You can delete this directory if you wish.")
    print("=======================================\n")

if __name__ == "__main__":
    run_demonstration()
