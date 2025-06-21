import json
import os
from datetime import datetime, timezone # Added timezone
from .dashboard_models import ServiceProfile, UserPrivacyProfile # Added UserPrivacyProfile
from typing import List # Import List from typing
from .policy_history_manager import POLICY_HISTORY_DIR # For consistency in user_data path logic
from urllib.parse import urlparse # To derive service_id/name from URL

USER_DATA_DIR = os.path.join(os.path.dirname(POLICY_HISTORY_DIR), 'user_data') # Puts it alongside, not inside policy_history
SERVICE_PROFILES_FILENAME = "service_profiles.json"
SERVICE_PROFILES_PATH = os.path.join(USER_DATA_DIR, SERVICE_PROFILES_FILENAME)

USER_PRIVACY_PROFILE_FILENAME = "user_privacy_profile.json"
USER_PRIVACY_PROFILE_PATH = os.path.join(USER_DATA_DIR, USER_PRIVACY_PROFILE_FILENAME)

def _ensure_user_data_dir_exists():
    os.makedirs(USER_DATA_DIR, exist_ok=True)

def get_service_id_from_source(source_url: str, policy_identifier: str) -> tuple[str, str]:
    """Derives a service_id and service_name from source_url or uses policy_identifier."""
    if source_url and source_url.lower().startswith('http'):
        try:
            parsed_url = urlparse(source_url)
            domain = parsed_url.netloc
            if domain:
                # Remove www. if present for consistency
                if domain.startswith('www.'):
                    domain = domain[4:]
                return domain, domain # Use domain as both id and name
        except Exception:
            pass # Fallback if URL parsing fails
    # For 'Pasted Text Input' or failed URL parse, use policy_identifier
    # This means each pasted text becomes a unique 'service' for now.
    # A future step would involve user input to name/group these.
    name = f"Pasted Analysis ({policy_identifier})"
    return policy_identifier, name

def load_service_profiles() -> List[ServiceProfile]:
    _ensure_user_data_dir_exists()
    if not os.path.exists(SERVICE_PROFILES_PATH):
        return []
    try:
        with open(SERVICE_PROFILES_PATH, 'r') as f:
            data = json.load(f)
            # Convert dicts back to ServiceProfile objects
            return [ServiceProfile(**sp_data) for sp_data in data]
    except (IOError, json.JSONDecodeError):
        print(f"Error loading or parsing {SERVICE_PROFILES_PATH}. Returning empty list.")
        return []

def save_service_profiles(service_profiles: List[ServiceProfile]):
    _ensure_user_data_dir_exists()
    try:
        # Convert ServiceProfile objects to dicts for JSON serialization
        data_to_save = [sp.__dict__ for sp in service_profiles]
        with open(SERVICE_PROFILES_PATH, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    except IOError as e:
        print(f"Error saving service profiles to {SERVICE_PROFILES_PATH}: {e}")

def update_or_create_service_profile(policy_analysis_data: dict):
    """
    Creates a new ServiceProfile or updates an existing one based on new policy_analysis_data.
    `policy_analysis_data` is the dict saved by policy_history_manager.save_policy_analysis.
    """
    if not policy_analysis_data:
        return

    policy_identifier = policy_analysis_data['policy_identifier']
    source_url = policy_analysis_data.get('source_url', 'Pasted Text Input')
    # service_id and auto_generated_service_name are derived based on source_url or policy_identifier
    service_id, auto_generated_service_name = get_service_id_from_source(source_url, policy_identifier)

    risk_assessment = policy_analysis_data.get('risk_assessment', {})
    profiles = load_service_profiles()
    existing_profile_index = -1
    existing_user_defined_name = None # Initialize

    for i, profile in enumerate(profiles):
        if profile.service_id == service_id:
            existing_profile_index = i
            existing_user_defined_name = profile.user_defined_name # Capture existing user-defined name
            break

    # Data for the profile, whether new or an update to an existing one
    profile_data_for_update = {
        'service_id': service_id,
        # service_name is the auto-generated one. user_defined_name will override display if set.
        'service_name': auto_generated_service_name,
        'user_defined_name': existing_user_defined_name, # Preserve or init to None if new
        'latest_analysis_timestamp': policy_analysis_data['analysis_timestamp'],
        'latest_policy_identifier': policy_identifier,
        'latest_service_risk_score': risk_assessment.get('service_risk_score', 0),
        'num_total_clauses': risk_assessment.get('num_clauses_analyzed', 0),
        'high_concern_count': risk_assessment.get('high_concern_count', 0),
        'medium_concern_count': risk_assessment.get('medium_concern_count', 0),
        'low_concern_count': risk_assessment.get('low_concern_count', 0),
        'source_url': source_url
    }

    if existing_profile_index != -1:
        # Existing profile found, check if this analysis is newer
        if policy_analysis_data['analysis_timestamp'] >= profiles[existing_profile_index].latest_analysis_timestamp:
            # Update existing profile, preserving its user_defined_name (already set in profile_data_for_update)
            profiles[existing_profile_index] = ServiceProfile(**profile_data_for_update)
            print(f"Service profile for '{auto_generated_service_name}' (ID: {service_id}) updated with newer analysis.")
        else:
            # This analysis is older, do not update the existing service profile's latest data
            print(f"Skipped update for service profile '{auto_generated_service_name}' (ID: {service_id}) as current analysis is older or same timestamp.")
            # No save needed if no change
            return # Exit early, no save needed
    else:
        # New service profile, user_defined_name will be None by default from profile_data_for_update
        new_profile = ServiceProfile(**profile_data_for_update)
        profiles.append(new_profile)
        print(f"New service profile for '{auto_generated_service_name}' (ID: {service_id}) created.")

    profiles.sort(key=lambda p: p.service_name) # Sort by auto-generated name for consistent file order
    save_service_profiles(profiles)

def get_all_service_profiles_for_dashboard() -> List[ServiceProfile]:
    """Loads all service profiles and sorts them for dashboard display."""
    profiles = load_service_profiles() # This already returns List[ServiceProfile]

    # Sort by latest_analysis_timestamp descending (most recent first)
    # Handle potential None or empty string timestamps if data can be corrupt, though load_service_profiles should ensure valid objects
    profiles.sort(key=lambda p: p.latest_analysis_timestamp if p.latest_analysis_timestamp else '', reverse=True)
    return profiles

def set_user_defined_name(service_id: str, new_user_name: str) -> bool:
    """Sets or updates the user_defined_name for a given service_id."""
    profiles = load_service_profiles()
    profile_found = False
    for profile in profiles:
        if profile.service_id == service_id:
            profile.user_defined_name = new_user_name.strip() if new_user_name else None # Store None if empty string after strip
            profile_found = True
            break

    if profile_found:
        save_service_profiles(profiles) # save_service_profiles already prints errors if IOError
        print(f"User-defined name for service ID '{service_id}' updated to '{new_user_name}'.")
        return True
    else:
        print(f"Service ID '{service_id}' not found. Cannot set user-defined name.")
        return False

def calculate_and_save_user_privacy_profile(user_id: str = "default_user") -> UserPrivacyProfile | None:
    _ensure_user_data_dir_exists()
    service_profiles = load_service_profiles() # Load all current service profiles

    if not service_profiles:
        # No services, create a default/empty UserPrivacyProfile
        profile = UserPrivacyProfile(
            user_id=user_id,
            overall_privacy_risk_score=None, # Or 0, depending on desired representation for no services
            key_privacy_insights=["No services analyzed yet."],
            total_services_analyzed=0,
            total_high_risk_services_count=0,
            total_medium_risk_services_count=0,
            total_low_risk_services_count=0,
            last_aggregated_at=datetime.now(timezone.utc).isoformat()
        )
        try:
            with open(USER_PRIVACY_PROFILE_PATH, 'w') as f:
                json.dump(profile.__dict__, f, indent=4)
            return profile
        except IOError as e:
            print(f"Error saving empty user privacy profile: {e}")
            return None

    total_services_analyzed = len(service_profiles)
    sum_of_risk_scores = 0
    total_high_risk_services = 0
    total_medium_risk_services = 0
    total_low_risk_services = 0

    # Insights generation can be more sophisticated later
    key_insights_list = [] # Use a list to control order and count

    for sp in service_profiles: # Ensure this loop is outside the initial `if not service_profiles:` block
        sum_of_risk_scores += sp.latest_service_risk_score
        if sp.latest_service_risk_score > 66:
            total_high_risk_services += 1
            # Use user_defined_name if available for the insight, otherwise the auto-generated service_name
            display_name = sp.user_defined_name if sp.user_defined_name else sp.service_name
            key_insights_list.append(f"{display_name} has a High privacy risk score ({sp.latest_service_risk_score}/100). Prioritize reviewing this service.")
        elif sp.latest_service_risk_score > 33:
            total_medium_risk_services += 1
        else:
            total_low_risk_services += 1

    overall_score = round(sum_of_risk_scores / total_services_analyzed) if total_services_analyzed > 0 else None

    # Refined insight logic based on overall score and counts
    if total_high_risk_services > 0:
        # The specific high-risk service insights are already added.
        # Could add a summary insight if there are many high-risk services.
        if total_high_risk_services > 1 and len(key_insights_list) < 3:
             key_insights_list.append(f"You have {total_high_risk_services} services with High risk scores. Focus on these first.")
    elif total_medium_risk_services > 0 and len(key_insights_list) < 3 : # Only show if no high risk ones, to reduce noise
        insight_text = f"You have {total_medium_risk_services} service(s) with a 'Medium' privacy risk score (34-66). It's advisable to review their details."
        if total_medium_risk_services == 1:
            display_name_medium = ""
            for sp_med in service_profiles: # Find the medium risk service
                if 33 < sp_med.latest_service_risk_score <= 66:
                    display_name_medium = sp_med.user_defined_name if sp_med.user_defined_name else sp_med.service_name
                    break
            insight_text = f"{display_name_medium if display_name_medium else 'A service'} has a 'Medium' privacy risk score ({sp_med.latest_service_risk_score}/100). It's advisable to review its details."
        key_insights_list.append(insight_text)

    # Add insight about overall posture if no specific high/medium risks are flagged by the above or list is still short
    if not key_insights_list or len(key_insights_list) < 2 :
        if overall_score is not None:
            if overall_score <= 33:
                key_insights_list.append("Your overall privacy posture appears relatively strong based on the services analyzed so far. Keep monitoring!")
            elif overall_score <= 66:
                key_insights_list.append("Your overall privacy posture is moderate. Review medium risk services and be mindful of new policies.")
            else: # overall_score > 66. Should have been caught by high_risk_services insight.
                key_insights_list.append("Your overall privacy posture has some high risk elements. Detailed review is recommended.")
        elif total_services_analyzed > 0:
             key_insights_list.append("Review individual service risk scores to understand your privacy posture.")

    if not key_insights_list and total_services_analyzed > 0:
        if total_low_risk_services == total_services_analyzed:
            key_insights_list.append("All currently analyzed services have Low privacy risk scores. Good job selecting services!")
        else:
             key_insights_list.append("Continue analyzing services to build a clearer picture of your privacy posture.")

    if not service_profiles: # This condition is handled at the start of the function now
        pass # Insights for empty profile are set at the function start
    elif not key_insights_list:
         key_insights_list.append("Review your dashboard for detailed service risk scores.")

    # Limit insights for display (e.g., max 3)
    final_insights = key_insights_list[:3]

    # Conceptual note for future AI integration (fulfills sub-issue 2.3 documentation part)
    # TODO: Future - Integrate advanced AI (e.g., LLM with specific prompts on aggregated data)
    # to synthesize more nuanced, natural language insights and actionable advice here.
    # Example: "Based on your preference to avoid data selling, the high risk score of Service X
    # (which mentions data selling) is a key concern. Consider finding an alternative or using opt-outs."

    user_profile = UserPrivacyProfile(
        user_id=user_id,
        overall_privacy_risk_score=overall_score,
        key_privacy_insights=final_insights, # Use the generated insights
        total_services_analyzed=total_services_analyzed,
        total_high_risk_services_count=total_high_risk_services,
        total_medium_risk_services_count=total_medium_risk_services,
        total_low_risk_services_count=total_low_risk_services,
        last_aggregated_at=datetime.now(timezone.utc).isoformat()
    )

    try:
        with open(USER_PRIVACY_PROFILE_PATH, 'w') as f:
            json.dump(user_profile.__dict__, f, indent=4)
        print(f"User privacy profile saved to: {USER_PRIVACY_PROFILE_PATH}")
        return user_profile
    except IOError as e:
        print(f"Error saving user privacy profile: {e}")
        return None

def load_user_privacy_profile(user_id: str = "default_user") -> UserPrivacyProfile | None:
    """Loads the UserPrivacyProfile from its JSON file."""
    if not os.path.exists(USER_PRIVACY_PROFILE_PATH):
        # If profile doesn't exist, calculate and save it for the first time.
        return calculate_and_save_user_privacy_profile(user_id)
    try:
        with open(USER_PRIVACY_PROFILE_PATH, 'r') as f:
            data = json.load(f)
            if 'user_id' not in data:
                print(f"Corrupted user profile file {USER_PRIVACY_PROFILE_PATH}, attempting to rebuild.")
                return calculate_and_save_user_privacy_profile(user_id)
            return UserPrivacyProfile(**data)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading user privacy profile from {USER_PRIVACY_PROFILE_PATH}: {e}. Attempting to rebuild.")
        return calculate_and_save_user_privacy_profile(user_id)

if __name__ == '__main__':
    print("Dashboard Data Manager - Service Profile Test")
    _ensure_user_data_dir_exists()
    # Clean up existing service_profiles.json for a clean test run
    if os.path.exists(SERVICE_PROFILES_PATH):
        os.remove(SERVICE_PROFILES_PATH)

    # Sample policy analysis data (mimicking what policy_history_manager saves)
    sample_analysis_1 = {
        'policy_identifier': '20240315100000001',
        'source_url': 'http://example.com/privacy',
        'analysis_timestamp': '2024-03-15T10:00:00.001Z',
        'full_policy_text': 'Example policy text.',
        'analysis_results': [],
        'risk_assessment': {
            'service_risk_score': 30, 'num_clauses_analyzed': 10,
            'high_concern_count': 1, 'medium_concern_count': 2, 'low_concern_count': 3
        }
    }
    sample_analysis_2_pasted = {
        'policy_identifier': '20240315110000002',
        'source_url': 'Pasted Text Input',
        'analysis_timestamp': '2024-03-15T11:00:00.002Z',
        'full_policy_text': 'Another example policy text, pasted by user.',
        'analysis_results': [],
        'risk_assessment': {
            'service_risk_score': 55, 'num_clauses_analyzed': 15,
            'high_concern_count': 2, 'medium_concern_count': 4, 'low_concern_count': 1
        }
    }
    # A newer analysis for example.com
    sample_analysis_3_example_updated = {
        'policy_identifier': '20240315120000003',
        'source_url': 'http://www.example.com/privacy_v2',
        'analysis_timestamp': '2024-03-15T12:00:00.003Z',
        'full_policy_text': 'Updated example policy text.',
        'analysis_results': [],
        'risk_assessment': {
            'service_risk_score': 25, 'num_clauses_analyzed': 12,
            'high_concern_count': 0, 'medium_concern_count': 1, 'low_concern_count': 5
        }
    }

    update_or_create_service_profile(sample_analysis_1)
    update_or_create_service_profile(sample_analysis_2_pasted)
    update_or_create_service_profile(sample_analysis_3_example_updated) # This should update example.com

    loaded_profiles = load_service_profiles()
    print(f"\nLoaded {len(loaded_profiles)} service profiles:")
    for p in loaded_profiles:
        print(f"  ID: {p.service_id}, Name: {p.service_name}, Score: {p.latest_service_risk_score}, Timestamp: {p.latest_analysis_timestamp}")

    # Expected: 2 profiles, example.com (updated) and the pasted one.
    if len(loaded_profiles) == 2:
        print("Test successful: Correct number of profiles.")
        found_example = any(prof.service_id == 'example.com' and prof.latest_service_risk_score == 25 for prof in loaded_profiles)
        if found_example:
            print("Test successful: example.com profile updated correctly.")
        else:
            print("Test FAILED: example.com profile not found or not updated.")
    else:
        print(f"Test FAILED: Expected 2 profiles, got {len(loaded_profiles)}.")

    print("\n--- Testing get_all_service_profiles_for_dashboard (sorted by timestamp desc) ---")
    # Create a third, earlier analysis for a new service to test sorting
    sample_analysis_0_very_old = {
        'policy_identifier': '20240315090000000', # Earlier ID
        'source_url': 'http://old-service.com/privacy',
        'analysis_timestamp': '2024-03-15T09:00:00.000Z', # Earlier timestamp
        'full_policy_text': 'Very old policy text.',
        'analysis_results': [],
        'risk_assessment': {
            'service_risk_score': 70, 'num_clauses_analyzed': 5,
            'high_concern_count': 3, 'medium_concern_count': 1, 'low_concern_count': 1
        }
    }
    update_or_create_service_profile(sample_analysis_0_very_old)

    dashboard_profiles = get_all_service_profiles_for_dashboard()
    print(f"\nLoaded {len(dashboard_profiles)} profiles for dashboard, sorted by timestamp:")
    for p in dashboard_profiles:
        print(f"  ID: {p.service_id}, Name: {p.service_name}, Score: {p.latest_service_risk_score}, Timestamp: {p.latest_analysis_timestamp}")

    if len(dashboard_profiles) == 3:
        print("Test successful: Correct number of profiles for dashboard.")
        # Check sorting: newest (sample_analysis_3_example_updated) should be first
        if dashboard_profiles[0].latest_policy_identifier == '20240315120000003':
            print("Test successful: Dashboard profiles sorted correctly by timestamp (desc).")
        else:
            print(f"Test FAILED: Dashboard profiles not sorted correctly. First item ID: {dashboard_profiles[0].latest_policy_identifier}")
        # Check that old-service.com is last
        if dashboard_profiles[2].service_id == 'old-service.com':
            print("Test successful: old-service.com is last as expected.")
        else:
            print(f"Test FAILED: old-service.com not last. Last item ID: {dashboard_profiles[2].service_id}")

    else:
        print(f"Test FAILED: Expected 3 profiles for dashboard, got {len(dashboard_profiles)}.")

    # Clean up again after __main__ tests
    if os.path.exists(SERVICE_PROFILES_PATH):
        os.remove(SERVICE_PROFILES_PATH)

    print("\n--- Testing UserPrivacyProfile calculation and loading ---")
    user_profile_instance = calculate_and_save_user_privacy_profile() # Uses profiles created above
    if user_profile_instance:
        print("User profile calculated and saved:")
        print(f"  Overall Score: {user_profile_instance.overall_privacy_risk_score}")
        print(f"  Total Services: {user_profile_instance.total_services_analyzed}")
        print(f"  High Risk Services: {user_profile_instance.total_high_risk_services_count}")
        print(f"  Insights: {user_profile_instance.key_privacy_insights}")

        loaded_user_profile = load_user_privacy_profile()
        if loaded_user_profile:
            print("User profile loaded successfully:")
            print(f"  Loaded Overall Score: {loaded_user_profile.overall_privacy_risk_score}")
            assert loaded_user_profile.overall_privacy_risk_score == user_profile_instance.overall_privacy_risk_score

    print("\n--- Testing set_user_defined_name ---")
    # Ensure 'example.com' exists from previous steps or create it
    if not any(p.service_id == 'example.com' for p in load_service_profiles()):
        update_or_create_service_profile(sample_analysis_1) # from previous main block setup

    if any(p.service_id == 'example.com' for p in load_service_profiles()):
        print("Attempting to rename 'example.com' to 'My Favorite Example Site'")
        rename_success = set_user_defined_name('example.com', 'My Favorite Example Site')
        if rename_success:
            renamed_profiles = load_service_profiles()
            renamed_found = False
            for p_renamed in renamed_profiles:
                if p_renamed.service_id == 'example.com':
                    print(f"  Found: ID='{p_renamed.service_id}', Name='{p_renamed.service_name}', UserDefinedName='{p_renamed.user_defined_name}'")
                    if p_renamed.user_defined_name == 'My Favorite Example Site':
                        print("  Rename successful and verified.")
                        renamed_found = True
                    else:
                        print("  Rename FAILED: user_defined_name did not update.")
                    break
            if not renamed_found:
                print("  Rename FAILED: 'example.com' not found after trying to rename.")
        else:
            print("  set_user_defined_name call returned False for 'example.com'.")

        print("Attempting to rename non-existent service 'foo.bar'")
        rename_fail_success = set_user_defined_name('foo.bar', 'No Such Service')
        if not rename_fail_success:
            print("  Correctly failed to rename non-existent service.")
        else:
            print("  Error: Renamed a non-existent service unexpectedly.")
    else:
        print("Skipping set_user_defined_name test in __main__ as 'example.com' was not found.")

    if os.path.exists(USER_PRIVACY_PROFILE_PATH):
        os.remove(USER_PRIVACY_PROFILE_PATH)
