import json
# --- Conceptual Data Models for Future Multi-Service Dashboard ---
# These models are for future planning and are not fully implemented in terms of aggregation yet.
# The current system saves individual policy analyses which contain the data needed for
# a 'ServiceEntry'.

# Conceptual: Represents a single analyzed service/policy in the dashboard list
# class ServiceEntry:
#     service_name: str  # User-defined or derived from URL
#     policy_identifier: str # The ID of the specific analysis version shown/latest
#     last_analysis_date: str # ISO timestamp
#     policy_version_identifier: str # Could be timestamp, or a hash of policy text
#     service_risk_score: int # The 0-100 score for this specific policy version
#     key_flagged_clauses_summary: List[str] # e.g., ["Mentions data selling (High Concern)", "Extensive cookie usage (Medium Concern)"]
#     source_url: str | None

# Conceptual: Represents the overall user privacy profile summary for the dashboard
# class PrivacyProfileSummary:
#     user_id: str # If multi-user support is added
#     overall_user_privacy_risk_score: int # Aggregated score from all services (0-100)
#     last_updated: str # ISO timestamp
#     services_analyzed: List[ServiceEntry] # List of all services/policies tracked
#     key_privacy_insights: List[str] # e.g., ["Multiple services share data for ads", "High risk from Service X"]
#     recent_policy_changes: List[dict] # Summary of recent significant policy changes across services

# The 'risk_assessment' dict saved by save_policy_analysis currently contains:
#   'overall_risk_score' (old sum-based score)
#   'service_risk_score' (new 0-100 normalized score for the policy)
#   'high_concern_count', 'medium_concern_count', 'low_concern_count', 'none_concern_count'
#   'num_clauses_analyzed'
# This 'service_risk_score' and the concern counts are key inputs for a ServiceEntry's score and insights.
# The 'policy_identifier' and 'analysis_timestamp' saved are also key for ServiceEntry.
# 'service_name' would likely come from user input when saving or from the source_url.

import os
import glob
from datetime import datetime, timezone

# Path setup assuming this file is in privacy_protocol/privacy_protocol/
POLICY_HISTORY_DIR = os.path.join(os.path.dirname(__file__), '..', 'policy_history')

def _ensure_history_dir_exists():
    os.makedirs(POLICY_HISTORY_DIR, exist_ok=True)

def generate_policy_identifier(user_input_name: str | None = None) -> str:
    """Generates a unique policy identifier, timestamp-based for now."""
    # For now, ignore user_input_name and always use timestamp for simplicity as per plan refinement.
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")[:-3] # Timestamp with milliseconds

def save_policy_analysis(identifier: str, policy_text: str, analysis_results: list, risk_assessment: dict, source_url: str | None = None) -> str | None:
    """
    Saves the policy text and its analysis results to a JSON file.
    The identifier is used as part of the filename.
    Returns the filename if successful, else None.
    """
    _ensure_history_dir_exists()
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    filename = f"{identifier}.json" # Identifier itself is the timestamp string
    filepath = os.path.join(POLICY_HISTORY_DIR, filename)

    data_to_save = {
        'policy_identifier': identifier,
        'source_url': source_url if source_url else 'text input',
        'analysis_timestamp': timestamp_iso,
        'full_policy_text': policy_text,
        'analysis_results': analysis_results,
        'risk_assessment': risk_assessment
    }

    try:
        with open(filepath, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Policy analysis saved to: {filepath}")
        return filename
    except IOError as e:
        print(f"Error saving policy analysis to {filepath}: {e}")
        return None

def list_analyzed_policies() -> list[dict]:
    """
    Lists all analyzed policies, returning metadata for each.
    Returns a list of dicts, each with 'identifier', 'timestamp', 'source_url'.
    Sorted by timestamp descending (most recent first).
    """
    _ensure_history_dir_exists()
    policy_files = glob.glob(os.path.join(POLICY_HISTORY_DIR, "*.json"))

    policies_metadata = []
    for policy_file_path in policy_files:
        try:
            with open(policy_file_path, 'r') as f:
                data = json.load(f)
                policies_metadata.append({
                    'identifier': data.get('policy_identifier'),
                    'timestamp': data.get('analysis_timestamp'),
                    'source_url': data.get('source_url', 'N/A')
                })
        except (IOError, json.JSONDecodeError, KeyError) as e:
            print(f"Error reading or parsing policy file {policy_file_path}: {e}")
            continue

    policies_metadata.sort(key=lambda p: p.get('timestamp', ''), reverse=True)
    return policies_metadata

def get_policy_analysis(identifier: str) -> dict | None:
    """
    Loads a specific policy analysis by its identifier (which is the filename without .json).
    """
    _ensure_history_dir_exists() # Ensure directory exists before trying to read
    filepath = os.path.join(POLICY_HISTORY_DIR, f"{identifier}.json")
    if not os.path.exists(filepath):
        print(f"Policy file not found: {filepath}")
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading policy analysis from {filepath}: {e}")
        return None

def get_latest_policy_analysis() -> dict | None:
    """
    Helper to get the most recently saved policy analysis.
    Returns None if no policies are saved.
    """
    all_policies = list_analyzed_policies()
    if not all_policies:
        return None
    latest_identifier = all_policies[0].get('identifier')
    if latest_identifier:
        return get_policy_analysis(latest_identifier)
    return None

if __name__ == '__main__':
    print("Policy History Manager Script")
    _ensure_history_dir_exists()
    print(f"Policy history directory: {POLICY_HISTORY_DIR}")

    print("\n--- Testing Save --- ")
    test_identifier = generate_policy_identifier()
    saved_file_name = save_policy_analysis( # Corrected variable name
        identifier=test_identifier,
        policy_text="This is a sample policy text for history.",
        analysis_results=[{'clause_text': 'Clause 1', 'ai_category': 'Other'}],
        risk_assessment={'overall_risk_score': 5}
    )
    if saved_file_name:
        print(f"Saved test analysis with ID: {test_identifier} to file: {saved_file_name}")
    else:
        print("Failed to save test analysis.")

    print("\n--- Testing List --- ")
    policies = list_analyzed_policies()
    if policies:
        print(f"Found {len(policies)} policy analyses:")
        for p_meta in policies:
            print(f"  ID: {p_meta['identifier']}, Timestamp: {p_meta['timestamp']}, Source: {p_meta['source_url']}")
    else:
        print("No policy analyses found in history.")

    print("\n--- Testing Load --- ")
    if policies:
        loaded_policy = get_policy_analysis(policies[0]['identifier'])
        if loaded_policy:
            print(f"Successfully loaded policy ID {loaded_policy['policy_identifier']}:")
            print(f"  Text snippet: {loaded_policy['full_policy_text'][:30]}...")
            print(f"  Risk score: {loaded_policy['risk_assessment']['overall_risk_score']}")
        else:
            print(f"Failed to load policy ID {policies[0]['identifier']}")
    else:
        print("Skipping load test as no policies were listed.")

    print("\n--- Testing Load Latest --- ")
    latest = get_latest_policy_analysis()
    if latest:
        print(f"Loaded latest policy with ID: {latest['policy_identifier']}")
    else:
        print("No latest policy found.")

    if saved_file_name and os.path.exists(os.path.join(POLICY_HISTORY_DIR, saved_file_name)): # Use corrected variable
        print(f"\nCleaning up test file: {saved_file_name}")
        os.remove(os.path.join(POLICY_HISTORY_DIR, saved_file_name))
