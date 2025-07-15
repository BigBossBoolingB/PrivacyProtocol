from dataclasses import dataclass
from typing import List

@dataclass
class PrivacyPolicy:
    """
    Represents a privacy policy with a unique ID, version, content, and a list of rules.
    """
    policy_id: str
    version: int
    content: str
    rules: List[str]
