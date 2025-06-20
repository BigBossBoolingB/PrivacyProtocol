from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ServiceProfile:
    service_id: str  # Unique identifier (e.g., domain for URLs, or policy_identifier for pasted text for now)
    service_name: str # This is the auto-derived name (domain or 'Pasted Analysis (id)')
    user_defined_name: Optional[str] = None # New field for user's custom name
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

    # No explicit to_dict/from_dict needed if using __dict__ for serialization
    # and **sp_data for deserialization with dataclasses, as long as new fields
    # have defaults or are handled by the loading logic if missing in old files.

@dataclass
class UserPrivacyProfile:
    user_id: str = "default_user" # Conceptual, unique to the user - for now, a single global profile
    overall_privacy_risk_score: Optional[int] = None # Numerical, 0-100, None if no services
    key_privacy_insights: List[str] = field(default_factory=list)
    total_services_analyzed: int = 0
    total_high_risk_services_count: int = 0
    total_medium_risk_services_count: int = 0
    total_low_risk_services_count: int = 0
    last_aggregated_at: Optional[str] = None # ISO timestamp string

    def __post_init__(self):
        # Ensure risk score is within bounds if not None
        if self.overall_privacy_risk_score is not None:
            self.overall_privacy_risk_score = max(0, min(100, int(self.overall_privacy_risk_score)))
