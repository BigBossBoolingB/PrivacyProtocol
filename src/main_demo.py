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
    from privacy_framework.obfuscation_engine import ObfuscationEngine
    from privacy_framework.privacy_enforcer import PrivacyEnforcer, PrivacyStatus # Added
    from demo_helpers.mock_data_generator import MockDataGenerator # Added
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
    # PROFILE_STORAGE_PATH = "user_profiles_demo/" # Not used in this version of demo
    POLICY_STORAGE_PATH = "_app_data_main_demo/policies/"
    CONSENT_STORAGE_PATH = "_app_data_main_demo/consents/"

    # Clean up storage from previous demo runs for consistency
    if os.path.exists("_app_data_main_demo/"):
        shutil.rmtree("_app_data_main_demo/")
    # Stores will create their specific subdirectories

    # --- 1. Initialize Core Components (including Stores) ---
    print("--- 1. Initializing Core Components ---")
    try:
        interpreter = PrivacyInterpreter() # Uses default 'en_core_web_sm'
        if not interpreter.nlp: # Should not happen if model downloaded, but good check
            print("ERROR: spaCy model for PrivacyInterpreter could not be loaded. Demo cannot proceed.")
            return
    except Exception as e: # Catch any other init error for interpreter
        print(f"ERROR: Failed to initialize PrivacyInterpreter: {e}. Demo cannot proceed.")
        return

    policy_store = PolicyStore(storage_path=POLICY_STORAGE_PATH)
    consent_store = ConsentStore(storage_path=CONSENT_STORAGE_PATH)

    # profile_manager = PrivacyProfileManager(storage_path=PROFILE_STORAGE_PATH) # Not actively used in this flow for now
    consent_manager = ConsentManager(consent_store=consent_store) # Inject store
    policy_evaluator = PolicyEvaluator()
    data_classifier = DataClassifier()
    obfuscation_engine = ObfuscationEngine()
    # Initialize new components for this demo
    mock_data_generator = MockDataGenerator(user_ids=[USER_ID]) # Generate data for our demo user
    privacy_enforcer = PrivacyEnforcer(
        data_classifier=data_classifier,
        policy_evaluator=policy_evaluator,
        obfuscation_engine=obfuscation_engine,
        consent_manager=consent_manager,
        policy_store=policy_store
    )
    print("Components initialized.\n")

    # --- 2. Define & Save a Sample Privacy Policy using PolicyStore ---
    print("--- 2. Defining & Saving a Sample Privacy Policy ---")
    demo_policy_obj = PrivacyPolicy( # Renamed to avoid conflict later
        policy_id="main_demo_policy_001",
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
        text_summary="Demo policy for main_demo.py, covering common data uses."
    )
    if policy_store.save_policy(demo_policy_obj):
        print(f"Saved PrivacyPolicy (ID: {demo_policy_obj.policy_id} v{demo_policy_obj.version}) to PolicyStore.\n")
    else:
        print(f"ERROR: Failed to save policy {demo_policy_obj.policy_id} to store. Demo might not reflect persistence.\n")


    # --- 3. Simulate User Granting Consent (Saved via ConsentManager/ConsentStore) ---
    print("--- 3. Simulating User Granting Consent ---")
    user_consent_obj = UserConsent( # Renamed to avoid conflict later
        consent_id=f"consent_{USER_ID}_{demo_policy_obj.policy_id}_{int(time.time())}",
        user_id=USER_ID,
        policy_id=demo_policy_obj.policy_id,
        version=demo_policy_obj.version,
        data_categories_consented=[
            DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.DEVICE_INFO
        ],
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS, Purpose.SECURITY],
        third_parties_consented=["trusted_analytics_partner.com"],
        is_active=True
    )
    if consent_manager.grant_consent(user_consent_obj): # Uses ConsentStore
        print(f"UserConsent (ID: {user_consent_obj.consent_id}) created and stored via ConsentManager.")
        print(f"  Consented Categories: {[dc.name for dc in user_consent_obj.data_categories_consented]}")
        print(f"  Consented Purposes: {[p.name for p in user_consent_obj.purposes_consented]}\n")
    else:
        print(f"ERROR: Failed to save consent {user_consent_obj.consent_id}. Demo might not reflect persistence.\n")

    # --- Simulate Application Restart & Load Data ---
    print("--- Simulating Application Restart: Initializing new Stores & Managers ---")
    policy_store_restarted = PolicyStore(storage_path=POLICY_STORAGE_PATH)
    consent_store_restarted = ConsentStore(storage_path=CONSENT_STORAGE_PATH)
    consent_manager_restarted = ConsentManager(consent_store=consent_store_restarted)

    # Load the policy
    loaded_policy = policy_store_restarted.load_policy(demo_policy_obj.policy_id, demo_policy_obj.version)
    if loaded_policy:
        print(f"Successfully reloaded policy: {loaded_policy.policy_id} v{loaded_policy.version}")
    else:
        print(f"ERROR: Failed to reload policy {demo_policy_obj.policy_id}. Aborting further demo.")
        return

    # Load the active consent for evaluation
    active_consent = consent_manager_restarted.get_active_consent(USER_ID, loaded_policy.policy_id)
    if not active_consent:
        print(f"ERROR: Could not retrieve active consent ({user_consent_obj.consent_id}) after restart. Demo cannot continue accurately.")
        return

    # --- 4. Sample Raw Data Generation & Processing via PrivacyEnforcer ---
    print("--- 4. Sample Raw Data Generation & Processing via PrivacyEnforcer ---")

    sample_data_records = [
        mock_data_generator.generate_user_activity_event(), # Might contain email
        mock_data_generator.generate_user_activity_event(),
        mock_data_generator.generate_sensor_reading() # Might contain location
    ]
    # Add a specific record with known PII for targeted testing
    sample_data_records.append({
        "event_id": str(uuid.uuid4()), "user_id": USER_ID, "action": "profile_update",
        "customer_email": "jane.doe@personal.com", "full_name": "Jane Personal Doe",
        "delivery_address": "123 Privacy Lane, Secret City", "timestamp": mock_data_generator._get_current_timestamp()
    })


    processing_scenarios = [
        {"purpose": Purpose.SERVICE_DELIVERY, "third_party": None, "description": "Core Service Functionality"},
        {"purpose": Purpose.MARKETING, "third_party": None, "description": "Internal Marketing"},
        {"purpose": Purpose.ANALYTICS, "third_party": "trusted_analytics_partner.com", "description": "Analytics with Trusted Partner"},
        {"purpose": Purpose.MARKETING, "third_party": "advertising_network.com", "description": "Ad Network Targeting"}
    ]

    for i, data_record in enumerate(sample_data_records):
        print(f"\n--- Processing Record {i+1} ---")
        print(f"Original Data Record:\n{json.dumps(data_record, indent=2)}")

        # Ensure the data_record has a user_id, or assign one for the demo if it's from a generic generator part
        current_user_id = data_record.get("user_id", USER_ID)
        if "user_id" not in data_record and "device_id" in data_record: # Sensor data might not have user_id
             # In a real system, device_id might be linkable to a user_id. For demo, assume it is.
             print(f"  (Note: Sensor data for device {data_record['device_id']}, associating with demo user {USER_ID})")


        for scen in processing_scenarios:
            print(f"\n  Scenario: {scen['description']} (Purpose: {scen['purpose'].name}, Third Party: {scen['third_party']})")

            enforcer_result = privacy_enforcer.process_data_record(
                user_id=current_user_id, # Use user_id from record or default
                policy_id=loaded_policy.policy_id,
                policy_version=loaded_policy.version,
                data_record=data_record,
                intended_purpose=scen["purpose"],
                intended_third_party=scen["third_party"]
            )

            print(f"  Enforcer Status: {enforcer_result['status'].name}")
            print(f"  Processed Data:\n{json.dumps(enforcer_result['processed_data'], indent=2, ensure_ascii=False)}")
            if enforcer_result['status'] != PrivacyStatus.PERMITTED_RAW:
                 print(f"  Message: {enforcer_result['message']}")


    print("\n--- 6. Demonstration Complete ---")
    # print(f"User profiles for this demo are stored in: {os.path.abspath(PROFILE_STORAGE_PATH)}") # Profile storage not used in this version of demo
    print(f"Policy data for this demo is in: {os.path.abspath(POLICY_STORAGE_PATH)}")
    print(f"Consent data for this demo is in: {os.path.abspath(CONSENT_STORAGE_PATH)}")
    print("You can delete the '_app_data_main_demo/' directory if you wish.")
    print("=======================================\n")

if __name__ == "__main__":
    run_demonstration()
