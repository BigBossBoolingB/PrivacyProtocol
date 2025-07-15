from .consent_store import ConsentStore
from .user_consent import UserConsent
import datetime

class ConsentManager:
    """
    Manages user consent, including granting, revoking, and checking consent status.
    """
    def __init__(self, consent_store: ConsentStore):
        """
        Initializes the ConsentManager.

        Args:
            consent_store (ConsentStore): The consent store to use for persistence.
        """
        self.consent_store = consent_store

    def grant_consent(self, user_id: str, policy_id: str, policy_version: int) -> UserConsent:
        """
        Grants consent for a user to a specific policy version.

        Args:
            user_id (str): The ID of the user.
            policy_id (str): The ID of the policy.
            policy_version (int): The version of the policy.

        Returns:
            UserConsent: The created consent object.
        """
        consent = UserConsent(
            consent_id=f"consent_{user_id}_{policy_id}",
            user_id=user_id,
            policy_id=policy_id,
            policy_version=policy_version,
            granted=True,
            timestamp=datetime.datetime.now()
        )

        # Conceptual placeholder for cryptographic signing.
        # This would use a private key associated with the user to sign the consent object.
        # This is a strategic link to DigiSocialBlock's identity system and EmPower1 Blockchain.
        # Example:
        # signed_consent = self.crypto_service.sign(consent, user_private_key)
        # self.consent_store.save_consent(signed_consent)

        self.consent_store.save_consent(consent)
        return consent

    def revoke_consent(self, user_id: str, policy_id: str):
        """
        Revokes a user's consent for a specific policy.

        Args:
            user_id (str): The ID of the user.
            policy_id (str): The ID of the policy.
        """
        latest_consent = self.consent_store.load_latest_consent(user_id, policy_id)
        if latest_consent:
            latest_consent.granted = False
            latest_consent.timestamp = datetime.datetime.now()
            self.consent_store.save_consent(latest_consent)

    def has_consent(self, user_id: str, policy_id: str) -> bool:
        """
        Checks if a user has active consent for a specific policy.

        Args:
            user_id (str): The ID of the user.
            policy_id (str): The ID of the policy.

        Returns:
            bool: True if the user has active consent, False otherwise.
        """
        latest_consent = self.consent_store.load_latest_consent(user_id, policy_id)
        return latest_consent is not None and latest_consent.granted
