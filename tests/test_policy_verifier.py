# tests/test_policy_verifier.py
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.policy import PrivacyPolicy, Purpose, LegalBasis, DataCategory
from src.privacy_framework.policy_verifier import PolicyVerifier

class TestPolicyVerifier(unittest.TestCase):

    def setUp(self):
        self.verifier = PolicyVerifier()
        self.sample_policy_marketing_ok = PrivacyPolicy(
            policy_id="p_mkt_ok", version=1,
            data_categories=[DataCategory.PERSONAL_INFO],
            purposes=[Purpose.MARKETING, Purpose.SERVICE_DELIVERY],
            legal_basis=LegalBasis.CONSENT,
            text_summary="Allows marketing",
            retention_period="1y",
            third_parties_shared_with=[]
        )
        self.sample_policy_no_marketing = PrivacyPolicy(
            policy_id="p_no_mkt", version=1,
            data_categories=[DataCategory.PERSONAL_INFO],
            purposes=[Purpose.SERVICE_DELIVERY],
            legal_basis=LegalBasis.CONSENT,
            text_summary="No marketing purpose",
            retention_period="1y",
            third_parties_shared_with=[]
        )
        self.sample_policy_indefinite_retention = PrivacyPolicy(
            policy_id="p_indef_ret", version=1,
            data_categories=[DataCategory.PERSONAL_INFO],
            purposes=[Purpose.SERVICE_DELIVERY],
            legal_basis=LegalBasis.CONSENT,
            text_summary="Indefinite retention",
            retention_period="indefinite",
            third_parties_shared_with=[]
        )
        self.sample_policy_no_retention = PrivacyPolicy(
            policy_id="p_no_ret", version=1,
            data_categories=[DataCategory.PERSONAL_INFO],
            purposes=[Purpose.SERVICE_DELIVERY],
            legal_basis=LegalBasis.CONSENT,
            text_summary="No retention defined",
            retention_period="", # Empty string
            third_parties_shared_with=[]
        )


    def test_verify_user_can_opt_out_marketing(self):
        # Policy includes marketing - conceptual check should pass (assumes opt-out is possible via consent)
        self.assertTrue(self.verifier.verify_policy_property(self.sample_policy_marketing_ok, "user_can_opt_out_marketing"))

        # Policy does not include marketing - property holds by default
        self.assertTrue(self.verifier.verify_policy_property(self.sample_policy_no_marketing, "user_can_opt_out_marketing"))

    def test_verify_data_retention_respected(self):
        # Policy has a defined, non-indefinite retention period
        self.assertTrue(self.verifier.verify_policy_property(self.sample_policy_marketing_ok, "data_retention_respected")) # Uses "1y"

        # Policy has indefinite retention - conceptual check might flag this
        self.assertFalse(self.verifier.verify_policy_property(self.sample_policy_indefinite_retention, "data_retention_respected"))

        # Policy has no retention period defined (empty string)
        self.assertFalse(self.verifier.verify_policy_property(self.sample_policy_no_retention, "data_retention_respected"))

    def test_verify_no_sensitive_data_for_analytics_placeholder(self):
        # This is a placeholder in the verifier, currently returns True
        self.assertTrue(self.verifier.verify_policy_property(self.sample_policy_marketing_ok, "no_sensitive_data_for_analytics_without_explicit_consent"))

    def test_verify_unknown_property(self):
        self.assertFalse(self.verifier.verify_policy_property(self.sample_policy_marketing_ok, "completely_unknown_property_xyz"))

if __name__ == '__main__':
    unittest.main()
