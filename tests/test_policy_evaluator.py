# tests/test_policy_evaluator.py
import unittest
import time

# Adjust import path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis
from src.privacy_framework.consent import UserConsent
from src.privacy_framework.data_attribute import DataAttribute, SensitivityLevel
from src.privacy_framework.policy_evaluator import PolicyEvaluator

class TestPolicyEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = PolicyEvaluator()
        self.user_id = "eval_user_001"
        self.policy_id = "eval_policy_001"
        self.ts_now = int(time.time())

        # Default Policy (Consent Based)
        self.consent_policy = PrivacyPolicy(
            policy_id=self.policy_id, version=1,
            data_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.DEVICE_INFO],
            purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS, Purpose.MARKETING],
            retention_period="1 year", third_parties_shared_with=["analytics.partner.com", "ads.partner.com"],
            legal_basis=LegalBasis.CONSENT, text_summary="Standard consent policy."
        )

        # Contractual Policy
        self.contract_policy = PrivacyPolicy(
            policy_id="contract_policy_002", version=1,
            data_categories=[DataCategory.PERSONAL_INFO, DataCategory.FINANCIAL_DATA],
            purposes=[Purpose.SERVICE_DELIVERY, Purpose.OPERATIONS], # No MARKETING by default
            retention_period="duration of contract", third_parties_shared_with=[],
            legal_basis=LegalBasis.CONTRACT, text_summary="Contractual obligations policy."
        )

        # Data Attributes
        self.email_attr = DataAttribute("email", DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, is_pii=True)
        self.usage_attr = DataAttribute("clicks", DataCategory.USAGE_DATA, SensitivityLevel.LOW)
        self.device_attr = DataAttribute("device_id", DataCategory.DEVICE_INFO, SensitivityLevel.MEDIUM)
        self.financial_attr = DataAttribute("cc_last_four", DataCategory.FINANCIAL_DATA, SensitivityLevel.CRITICAL)

    def _create_sample_consent(self, policy_id, version, data_cats, purposes, third_parties=None, is_active=True):
        return UserConsent(
            consent_id=f"consent_{policy_id}_{int(time.time()*1000)}", # Unique enough
            user_id=self.user_id,
            policy_id=policy_id,
            version=version,
            data_categories_consented=data_cats,
            purposes_consented=purposes,
            third_parties_consented=third_parties if third_parties is not None else [],
            is_active=is_active,
            timestamp=self.ts_now
        )

    # --- Consent-Based Policy Tests ---
    def test_permitted_by_consent_policy_and_consent(self):
        consent = self._create_sample_consent(
            self.policy_id, 1,
            [DataCategory.PERSONAL_INFO], [Purpose.MARKETING]
        )
        self.assertTrue(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.email_attr], Purpose.MARKETING
        ))

    def test_denied_purpose_not_in_consent_policy(self):
        # RESEARCH is not in self.consent_policy.purposes
        consent = self._create_sample_consent(
            self.policy_id, 1,
            [DataCategory.PERSONAL_INFO], [Purpose.RESEARCH] # User consents to research
        )
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.email_attr], Purpose.RESEARCH
        ))

    def test_denied_consent_missing_for_consent_policy(self):
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.consent_policy, None, [self.email_attr], Purpose.MARKETING
        ))

    def test_denied_consent_inactive_for_consent_policy(self):
        consent = self._create_sample_consent(
            self.policy_id, 1,
            [DataCategory.PERSONAL_INFO], [Purpose.MARKETING], is_active=False
        )
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.email_attr], Purpose.MARKETING
        ))

    def test_denied_consent_wrong_policy_id(self):
        consent = self._create_sample_consent(
            "wrong_policy_id", 1, # Policy ID mismatch
            [DataCategory.PERSONAL_INFO], [Purpose.MARKETING]
        )
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.email_attr], Purpose.MARKETING
        ))

    def test_denied_consent_wrong_policy_version(self):
        consent = self._create_sample_consent(
            self.policy_id, 0, # Policy version mismatch
            [DataCategory.PERSONAL_INFO], [Purpose.MARKETING]
        )
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.email_attr], Purpose.MARKETING
        ))

    def test_denied_data_category_not_in_consent(self):
        consent = self._create_sample_consent(
            self.policy_id, 1,
            [DataCategory.USAGE_DATA], [Purpose.MARKETING] # Consents USAGE, but operation uses PERSONAL_INFO
        )
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.email_attr], Purpose.MARKETING
        ))

    def test_denied_purpose_not_in_consent(self):
        consent = self._create_sample_consent(
            self.policy_id, 1,
            [DataCategory.PERSONAL_INFO], [Purpose.SERVICE_DELIVERY] # Consents SD, but operation is MARKETING
        )
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.email_attr], Purpose.MARKETING
        ))

    def test_third_party_sharing_permitted(self):
        consent = self._create_sample_consent(
            self.policy_id, 1,
            [DataCategory.DEVICE_INFO], [Purpose.ANALYTICS],
            third_parties=["analytics.partner.com"]
        )
        self.assertTrue(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.device_attr], Purpose.ANALYTICS, "analytics.partner.com"
        ))

    def test_third_party_sharing_denied_not_in_consent_list(self):
        consent = self._create_sample_consent(
            self.policy_id, 1,
            [DataCategory.DEVICE_INFO], [Purpose.ANALYTICS],
            third_parties=["another.partner.com"] # Consented to a different partner
        )
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.device_attr], Purpose.ANALYTICS, "analytics.partner.com"
        ))

    def test_third_party_sharing_denied_consent_list_empty(self):
        consent = self._create_sample_consent(
            self.policy_id, 1,
            [DataCategory.DEVICE_INFO], [Purpose.ANALYTICS],
            third_parties=[] # Empty list means no third-party sharing explicitly consented for this record
        )
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.device_attr], Purpose.ANALYTICS, "analytics.partner.com"
        ))

    def test_third_party_sharing_not_proposed_operation_permitted(self):
        # Operation does not involve third party, should pass if other conditions met
        consent = self._create_sample_consent(
            self.policy_id, 1,
            [DataCategory.PERSONAL_INFO], [Purpose.SERVICE_DELIVERY]
        )
        self.assertTrue(self.evaluator.is_operation_permitted(
            self.consent_policy, consent, [self.email_attr], Purpose.SERVICE_DELIVERY, None # No third party proposed
        ))

    # --- Contract-Based Policy Tests (Simplified V1 Logic) ---
    def test_permitted_contract_basis_service_delivery_no_consent_obj(self):
        # For CONTRACT, SERVICE_DELIVERY is allowed if policy lists it, even with consent=None
        self.assertTrue(self.evaluator.is_operation_permitted(
            self.contract_policy, None, [self.email_attr], Purpose.SERVICE_DELIVERY
        ))

    def test_denied_contract_basis_purpose_not_in_policy(self):
        # MARKETING is not in self.contract_policy.purposes
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.contract_policy, None, [self.email_attr], Purpose.MARKETING
        ))

    def test_permitted_contract_basis_other_purpose_in_policy_no_consent_obj(self):
        # OPERATIONS is in self.contract_policy.purposes
        # Current simplified logic for non-consent basis: if purpose in policy, it's allowed.
        self.assertTrue(self.evaluator.is_operation_permitted(
            self.contract_policy, None, [self.financial_attr], Purpose.OPERATIONS
        ))

    def test_contract_basis_with_irrelevant_consent(self):
        # If a consent object is provided but policy is CONTRACT, consent checks are bypassed by current logic
        # for non-LegalBasis.CONSENT. The operation should still be judged by policy.
        irrelevant_consent = self._create_sample_consent(
            self.contract_policy.policy_id, self.contract_policy.version,
            [DataCategory.USAGE_DATA], [Purpose.ANALYTICS] # Consent for things not related to operation
        )
        self.assertTrue(self.evaluator.is_operation_permitted(
            self.contract_policy, irrelevant_consent, [self.email_attr], Purpose.SERVICE_DELIVERY
        ))

        # If policy doesn't allow the purpose, it should still be denied
        self.assertFalse(self.evaluator.is_operation_permitted(
            self.contract_policy, irrelevant_consent, [self.email_attr], Purpose.MARKETING # MARKETING not in contract_policy
        ))

if __name__ == '__main__':
    unittest.main()
