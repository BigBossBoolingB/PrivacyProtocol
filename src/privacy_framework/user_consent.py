from dataclasses import dataclass
import datetime

@dataclass
class UserConsent:
    consent_id: str
    user_id: str
    policy_id: str
    policy_version: int
    granted: bool
    timestamp: datetime.datetime
