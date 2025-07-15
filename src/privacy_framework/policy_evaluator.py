from .privacy_policy import PrivacyPolicy
from .user_consent import UserConsent

class PolicyEvaluator:
    @staticmethod
    def is_purpose_permitted(policy: PrivacyPolicy, consent: UserConsent, purpose: str) -> bool:
        """
        Checks if the intended purpose is permitted by the policy and consent.
        For demonstration, it uses a simple rule-based evaluation.
        """
        if not consent.granted:
            return False

        # Example rule: Allow analytics if the policy contains the "allow_analytics" rule
        if purpose == "Analytics" and "allow_analytics" in policy.rules:
            return True

        # Example rule: Allow marketing if the policy contains the "allow_marketing" rule
        if purpose == "Marketing" and "allow_marketing" in policy.rules:
            return True

        return False
