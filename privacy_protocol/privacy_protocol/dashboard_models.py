from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ServiceProfile:
    service_id: str  # Unique identifier (e.g., domain for URLs, or policy_identifier for pasted text for now)
    service_name: str # Display name (e.g., domain or user-defined, or policy_identifier for now)
    latest_analysis_timestamp: str # ISO string from the latest policy analysis
    latest_policy_identifier: str # The policy_identifier of the latest analysis in history
    latest_service_risk_score: int # The 0-100 score from the latest analysis
    num_total_clauses: int # From latest analysis
    high_concern_count: int
    medium_concern_count: int
    low_concern_count: int
    # Optional: Add a very short summary of key flagged clauses if easily derivable, or defer.
    # key_flagged_clauses_summary: List[str] = field(default_factory=list)
    source_url: Optional[str] = None # Original source URL if available

# --- Conceptual: UserPrivacyProfile (Future Full Implementation) ---
# @dataclass
# class UserPrivacyProfile:
#     user_id: str # Or some session identifier if single user for now
#     overall_user_privacy_risk_score: Optional[int] = None # e.g., 0-100, average or weighted
#     last_calculated: Optional[str] = None # ISO timestamp
#     # The list of service profiles is what get_all_service_profiles_for_dashboard() currently provides.
#     # In a full model, this might be stored here or fetched.
#     # service_profiles: List[ServiceProfile] = field(default_factory=list)
#     key_overall_privacy_insights: List[str] = field(default_factory=list)
#     # Example insights: "3 services engage in data selling.", "Average service risk score is Medium (55)."

# For the current implementation phase, the `get_all_service_profiles_for_dashboard()` function
# in `dashboard_data_manager.py` provides the list of service profiles that will populate the dashboard.
# An aggregated UserPrivacyProfile object stored separately is deferred.
