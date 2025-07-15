from .consent_store import ConsentStore
from .user_consent import UserConsent
import datetime

class ConsentManager:
    def __init__(self, consent_store: ConsentStore):
        self.consent_store = consent_store

    def grant_consent(self, user_id: str, policy_id: str, policy_version: int) -> UserConsent:
        consent = UserConsent(
            consent_id=f"consent_{user_id}_{policy_id}",
            user_id=user_id,
            policy_id=policy_id,
            policy_version=policy_version,
            granted=True,
            timestamp=datetime.datetime.now()
        )
        self.consent_store.save_consent(consent)
        return consent

    def revoke_consent(self, user_id: str, policy_id: str):
        latest_consent = self.consent_store.load_latest_consent(user_id, policy_id)
        if latest_consent:
            latest_consent.granted = False
            latest_consent.timestamp = datetime.datetime.now()
            self.consent_store.save_consent(latest_consent)

    def has_consent(self, user_id: str, policy_id: str) -> bool:
        latest_consent = self.consent_store.load_latest_consent(user_id, policy_id)
        return latest_consent is not None and latest_consent.granted
