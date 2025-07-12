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


from src.privacy_framework.formal_policies import FORMAL_POLICY_RULES # Import the actual rules

class TestPolicyVerifier(unittest.TestCase):

    def setUp(self):
        # Verifier will load default rules from formal_policies.py
        self.verifier = PolicyVerifier()

        self.compliant_policy = PrivacyPolicy( # Designed to pass most conceptual rules
            policy_id="p_compliant", version=1,
            data_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
            purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS], # No MARKETING by default for this one
            legal_basis=LegalBasis.CONSENT,
            text_summary="A generally compliant policy.",
            retention_period="365 days",
            third_parties_shared_with=["some_analytics_partner.com"]
        )
        self.policy_with_marketing = PrivacyPolicy(
            policy_id="p_mkt", version=1,
            data_categories=[DataCategory.PERSONAL_INFO, DataCategory.HEALTH_DATA], # Includes HEALTH_DATA
            purposes=[Purpose.SERVICE_DELIVERY, Purpose.MARKETING],
            legal_basis=LegalBasis.CONSENT,
            text_summary="Policy with marketing and health data.",
            retention_period="1 year",
            third_parties_shared_with=["partner_A", "ThirdParty_X"] # Includes ThirdParty_X
        )
        self.policy_violates_retention = PrivacyPolicy(
            policy_id="p_bad_retention", version=1,
            data_categories=[DataCategory.USAGE_DATA],
            purposes=[Purpose.ANALYTICS],
            legal_basis=LegalBasis.CONSENT,
            text_summary="Policy with indefinite retention for analytics.",
            retention_period="indefinite",
            third_parties_shared_with=[]
        )

    def test_verify_compliant_policy(self):
        results = self.verifier.verify_policy_adherence(self.compliant_policy)
        # Based on current conceptual rules in formal_policies.py and PolicyVerifier logic:
        # FP001 (PII Marketing): Vacuously true as no MARKETING purpose.
        # FP002 (Retention for Analytics UD): True, "365 days" is not empty or "indefinite".
        # FP003 (PII for Analytics): Vacuously true as PI is for SD, not directly for Analytics in this policy's purpose list for PI.
        # FP004 (Health Data with ThirdParty_X): Vacuously true as no HEALTH_DATA.
        # FP005 (Marketing implies opt-out): Vacuously true as no MARKETING.
        for rule_id, adhered in results.items():
            self.assertTrue(adhered, f"Rule {rule_id} should adhere for compliant_policy but was {adhered}")

    def test_verify_policy_with_marketing_and_health_data_violations(self):
        results = self.verifier.verify_policy_adherence(self.policy_with_marketing)

        # FP001 (PII Marketing): Should hold conceptually because legal_basis is CONSENT.
        self.assertTrue(results.get("FP001", False), "FP001: Marketing with PI implies consent should be possible.")

        # FP004 (Health Data with ThirdParty_X): This policy *shares* with ThirdParty_X and *has* HEALTH_DATA.
        # The rule asserts "not_contains" ThirdParty_X if HEALTH_DATA is present.
        # So, this rule should FAIL for this policy.
        self.assertFalse(results.get("FP004", True), "FP004: Should detect Health_Data shared with restricted ThirdParty_X.")

        # FP005 (Marketing implies opt-out): Should hold as legal_basis is CONSENT.
        self.assertTrue(results.get("FP005", False), "FP005: Marketing purpose with CONSENT basis should pass.")

    def test_verify_policy_violates_retention_rule(self):
        results = self.verifier.verify_policy_adherence(self.policy_violates_retention)
        # FP002 (Retention for Analytics UD): Policy has "indefinite" retention.
        # The conceptual check for "is_reasonable_for_analytics_usage_data" fails for "indefinite".
        self.assertFalse(results.get("FP002", True), "FP002: Indefinite retention for analytics usage data should fail.")

    def test_verifier_with_no_rules(self):
        empty_verifier = PolicyVerifier(formal_rules=[])
        results = empty_verifier.verify_policy_adherence(self.compliant_policy)
        self.assertEqual(len(results), 0) # No rules, no results.

    def test_verifier_with_custom_rule_pass(self):
        custom_rules = [{
            "rule_id": "CR001", "description": "Test custom pass", "applies_to_policy_itself": True,
            "conditions": [{"field": "policy_id", "operator": "contains", "value": "custom_pass"}],
            "assertion": {"constraint": "always_true_for_test"} # Verifier needs to handle this
        }]
        # Add a way for PolicyVerifier to handle conceptual 'always_true_for_test' or make conditions specific
        # For simplicity, let's make the assertion directly checkable.
        custom_rules[0]["assertion"] = {"field": "version", "operator": "contains", "value": 1} # Assuming version is int, 'contains' is not ideal.
                                                                                                # Let's assume _check_condition handles int equality for 'contains' for demo.
                                                                                                # Or add an 'equals' operator.

        # For now, let's make a rule that's easy to pass with current verifier
        custom_rules_pass = [{
            "rule_id": "CR001_PASS", "description": "Custom rule that passes",
            "applies_to_policy_itself": True,
            "conditions": [{"field": "policy_id", "operator": "contains", "value": "p_compliant"}], # policy_id is string
            "assertion": {"field": "version", "operator": "equals_int", "value": 1} # Need 'equals_int'
        }]

        # Temporarily add 'equals_int' to verifier for this test or modify rule
        original_check_condition = PolicyVerifier._check_condition
        def mock_check_condition(self_obj, policy_field_value, operator, condition_value):
            if operator == "equals_int":
                return policy_field_value == condition_value
            return original_check_condition(self_obj, policy_field_value, operator, condition_value)

        with unittest.mock.patch.object(PolicyVerifier, '_check_condition', new=mock_check_condition):
            verifier_custom = PolicyVerifier(formal_rules=custom_rules_pass)
            results = verifier_custom.verify_policy_adherence(self.compliant_policy)
            self.assertTrue(results.get("CR001_PASS", False))


if __name__ == '__main__':
    unittest.main()
