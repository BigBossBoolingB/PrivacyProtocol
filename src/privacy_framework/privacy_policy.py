from dataclasses import dataclass
from typing import List

@dataclass
class PrivacyPolicy:
    policy_id: str
    version: int
    content: str
    rules: List[str]
