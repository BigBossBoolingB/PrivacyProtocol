from dataclasses import dataclass
import datetime

@dataclass
class UserConsent:
    """
    Represents a user's consent to a specific version of a privacy policy.
    """
    consent_id: str
    user_id: str
    policy_id: str
    policy_version: int
    granted: bool
    timestamp: datetime.datetime
