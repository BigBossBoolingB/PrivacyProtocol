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
    from privacy_framework.data_classifier import DataClassifier
    from privacy_framework.obfuscation_engine import ObfuscationEngine, ObfuscationMethod
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
    data_classifier = DataClassifier()
    obfuscation_engine = ObfuscationEngine()
    print("Components initialized.\n")

    # --- 2. Define a Sample Privacy Policy ---
    print("--- 2. Defining a Sample Privacy Policy ---")
    demo_policy = PrivacyPolicy(
        policy_id="demo_policy_002",
        version=1,
        data_categories=[
            DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA,
            DataCategory.DEVICE_INFO, DataCategory.LOCATION_DATA
        ],
        purposes=[
            Purpose.SERVICE_DELIVERY, Purpose.MARKETING,
            Purpose.ANALYTICS, Purpose.IMPROVEMENT, Purpose.SECURITY
        ],
        retention_period="1 year",
        third_parties_shared_with=["trusted_analytics_partner.com", "advertising_network.com"],
        legal_basis=LegalBasis.CONSENT,
        text_summary="Demo policy covering common data uses."
    )
    print(f"Defined PrivacyPolicy object (ID: {demo_policy.policy_id}).\n")

    # --- 3. Simulate User Granting Consent ---
    print("--- 3. Simulating User Granting Consent ---")
    # User wants Service Delivery & Analytics, but NOT Marketing for their Personal Info.
    # They are okay with sharing Usage/Device data with trusted_analytics_partner.com for Analytics.
    user_consent_for_demo_policy = UserConsent(
        consent_id=f"consent_{USER_ID}_{demo_policy.policy_id}_{int(time.time())}",
        user_id=USER_ID,
        policy_id=demo_policy.policy_id,
        version=demo_policy.version,
        data_categories_consented=[
            DataCategory.PERSONAL_INFO, # For Service Delivery
            DataCategory.USAGE_DATA,    # For Analytics
            DataCategory.DEVICE_INFO    # For Analytics & Security
        ],
        purposes_consented=[
            Purpose.SERVICE_DELIVERY, # For PI, Usage, Device
            Purpose.ANALYTICS,        # For Usage, Device
            Purpose.SECURITY          # For Device
        ],
        third_parties_consented=["trusted_analytics_partner.com"], # Only this partner
        is_active=True
    )
    consent_manager.store_consent(user_consent_for_demo_policy)
    print(f"UserConsent (ID: {user_consent_for_demo_policy.consent_id}) created and stored.")
    print(f"  Consented Categories: {[dc.name for dc in user_consent_for_demo_policy.data_categories_consented]}")
    print(f"  Consented Purposes: {[p.name for p in user_consent_for_demo_policy.purposes_consented]}")
    print(f"  Consented Third Parties: {user_consent_for_demo_policy.third_parties_consented}\n")

    active_consent = consent_manager.get_active_consent(USER_ID, demo_policy.policy_id)
    if not active_consent:
        print("ERROR: Could not retrieve active consent. Demo cannot continue accurately.")
        return

    # --- 4. Sample Raw Data & Classification ---
    print("--- 4. Sample Raw Data & Classification ---")
    sample_raw_data = {
        "full_name": "Jane Doe",
        "email_address": "jane.doe@example.com",
        "primary_phone": "555-012-3456",
        "last_login_ip": "203.0.113.45",
        "last_purchase_category": "electronics",
        "user_agent_string": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
        "current_city": "New York"
    }
    print(f"Sample Raw Data:\n{json.dumps(sample_raw_data, indent=2)}\n")

    classified_attributes = data_classifier.classify_data(sample_raw_data)
    print("Classified Data Attributes:")
    attr_map_for_demo = {}
    for attr in classified_attributes:
        print(f"  - {attr.attribute_name}: Category={attr.category.name}, Sensitivity={attr.sensitivity_level.name}, PII={attr.is_pii}, ObfPref={attr.obfuscation_method_preferred.name}")
        attr_map_for_demo[attr.attribute_name] = attr
    print("")

    # --- 5. End-to-End Data Operation Evaluation & Obfuscation ---
    print("--- 5. End-to-End Data Operation Evaluation & Obfuscation ---")

    scenarios = [
        {
            "name": "Display User Profile (Service Delivery)",
            "purpose": Purpose.SERVICE_DELIVERY,
            "third_party": None,
            "data_to_process": {"full_name": sample_raw_data["full_name"], "email_address": sample_raw_data["email_address"]}
        },
        {
            "name": "Send Marketing Email (Marketing)",
            "purpose": Purpose.MARKETING,
            "third_party": None,
            "data_to_process": {"email_address": sample_raw_data["email_address"]}
        },
        {
            "name": "Internal Security Logging (Security)",
            "purpose": Purpose.SECURITY,
            "third_party": None,
            "data_to_process": {"last_login_ip": sample_raw_data["last_login_ip"]}
        },
        {
            "name": "Share Usage Data with Analytics Partner (Analytics)",
            "purpose": Purpose.ANALYTICS,
            "third_party": "trusted_analytics_partner.com",
            "data_to_process": {"last_purchase_category": sample_raw_data["last_purchase_category"], "user_agent_string": sample_raw_data["user_agent_string"], "current_city": sample_raw_data["current_city"]}
        },
        {
            "name": "Share Data with Unapproved Ad Network (Marketing)",
            "purpose": Purpose.MARKETING,
            "third_party": "advertising_network.com", # Policy allows, but consent might not
            "data_to_process": {"email_address": sample_raw_data["email_address"], "current_city": sample_raw_data["current_city"]}
        }
    ]

    for scenario_index, scenario in enumerate(scenarios):
        print(f"\n--- Scenario {scenario_index + 1}: {scenario['name']} ---")
        print(f"  Proposed Purpose: {scenario['purpose'].name}")
        if scenario['third_party']:
            print(f"  Proposed Third Party: {scenario['third_party']}")
        print(f"  Data involved (original): {scenario['data_to_process']}")

        # For each field in this scenario's data_to_process, we need its classification
        scenario_attributes = []
        for key in scenario['data_to_process'].keys():
            if key in attr_map_for_demo: # Use the globally classified attribute for this key
                scenario_attributes.append(attr_map_for_demo[key])
            else: # Should not happen if data_to_process keys are from sample_raw_data
                print(f"Warning: Key '{key}' not found in initial classification for scenario.")
                # Create a default 'OTHER' attribute if missing
                scenario_attributes.append(DataAttribute(key, DataCategory.OTHER, SensitivityLevel.LOW))


        processed_scenario_data = obfuscation_engine.process_data_attributes(
            raw_data=scenario['data_to_process'],
            classified_attributes=scenario_attributes, # Pass only relevant attributes
            policy=demo_policy,
            consent=active_consent,
            proposed_purpose=scenario['purpose'],
            policy_evaluator=policy_evaluator,
            proposed_third_party=scenario['third_party']
        )
        print(f"  Processed Data: {json.dumps(processed_scenario_data, indent=2)}")

        # Add a small explanation of why fields might be obfuscated
        for key, val in processed_scenario_data.items():
            original_val = scenario['data_to_process'].get(key)
            if val != original_val:
                attr_for_key = next((a for a in scenario_attributes if a.attribute_name == key), None)
                if attr_for_key:
                     is_perm = policy_evaluator.is_operation_permitted(demo_policy, active_consent, [attr_for_key], scenario['purpose'], scenario['third_party'])
                     print(f"    - Field '{key}': Original='{original_val}', Processed='{val}'. Permission: {'Granted' if is_perm else 'Denied -> Obfuscated'}")
                else:
                     print(f"    - Field '{key}': Original='{original_val}', Processed='{val}'. (Attribute details not found for explanation)")


    print("\n--- 6. Demonstration Complete ---")
    print(f"User profiles for this demo are stored in: {os.path.abspath(PROFILE_STORAGE_PATH)}") # Profile storage not used in this version of demo
    print("=======================================\n")

if __name__ == "__main__":
    run_demonstration()
