import unittest
from privacy_protocol_core.auditing.policy_verifier import PolicyVerifier
from privacy_protocol_core.policy import PrivacyPolicy, Purpose, DataCategory # Assuming these are accessible

class TestPolicyVerifier(unittest.TestCase):

    def setUp(self):
        self.verifier = PolicyVerifier()
        # Create a base policy for testing, can be modified per test
        self.sample_policy_dict = {
            "policy_id": "test_pv_policy",
            "version": "1.0",
            "data_categories": ["Personal_Info", "Usage_Data"],
            "purposes": ["Service_Delivery", "Analytics"],
            "retention_period": "1 year",
            "text_summary": "We use personal info for service delivery. You can contact us about privacy."
        }
        self.policy = PrivacyPolicy.from_dict(self.sample_policy_dict)

    def test_verify_opt_out_possible_for_marketing(self):
        # Scenario 1: Marketing is a purpose, opt-out mentioned in summary
        self.policy.purposes.append(Purpose.MARKETING)
        self.policy.text_summary += " You can opt-out of marketing communications."
        results = self.verifier.verify_policy_properties(self.policy, ["opt_out_possible_for_marketing"])
        self.assertTrue(results.get("opt_out_possible_for_marketing"))

        # Scenario 2: Marketing is a purpose, no opt-out mentioned
        self.policy.text_summary = "We use data for marketing." # Opt-out not mentioned
        results_no_opt_out = self.verifier.verify_policy_properties(self.policy, ["opt_out_possible_for_marketing"])
        self.assertFalse(results_no_opt_out.get("opt_out_possible_for_marketing"))

        # Scenario 3: Marketing is not a purpose
        self.policy.purposes = [Purpose.SERVICE_DELIVERY] # Remove marketing
        self.policy.text_summary = "Service delivery only."
        results_no_marketing = self.verifier.verify_policy_properties(self.policy, ["opt_out_possible_for_marketing"])
        self.assertTrue(results_no_marketing.get("opt_out_possible_for_marketing")) # Trivially true

    def test_verify_data_minimization_for_analytics(self):
        # Scenario 1: Analytics purpose, few data categories (placeholder: < 5 and includes USAGE_DATA)
        self.policy.purposes = [Purpose.ANALYTICS]
        self.policy.data_categories = [DataCategory.USAGE_DATA, DataCategory.TECHNICAL_INFO] # 2 categories
        results = self.verifier.verify_policy_properties(self.policy, ["data_minimization_for_analytics"])
        self.assertTrue(results.get("data_minimization_for_analytics"))

        # Scenario 2: Analytics purpose, many data categories
        self.policy.data_categories = [DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.TECHNICAL_INFO, DataCategory.LOCATION_DATA, DataCategory.FINANCIAL_INFO] # 5 categories
        results_many_cats = self.verifier.verify_policy_properties(self.policy, ["data_minimization_for_analytics"])
        self.assertFalse(results_many_cats.get("data_minimization_for_analytics"))

        # Scenario 3: Analytics not a purpose
        self.policy.purposes = [Purpose.SERVICE_DELIVERY]
        results_no_analytics = self.verifier.verify_policy_properties(self.policy, ["data_minimization_for_analytics"])
        self.assertTrue(results_no_analytics.get("data_minimization_for_analytics")) # Trivially true

    def test_verify_retention_limits_defined_for_pii(self):
        # Scenario 1: PII collected, specific retention period
        self.policy.data_categories = [DataCategory.PERSONAL_INFO]
        self.policy.retention_period = "90 days"
        results = self.verifier.verify_policy_properties(self.policy, ["retention_limits_defined_for_pii"])
        self.assertTrue(results.get("retention_limits_defined_for_pii"))

        # Scenario 2: PII collected, "Not Specified" retention
        self.policy.retention_period = "Not Specified"
        results_not_specified = self.verifier.verify_policy_properties(self.policy, ["retention_limits_defined_for_pii"])
        self.assertFalse(results_not_specified.get("retention_limits_defined_for_pii"))

        # Scenario 3: No PII collected (only USAGE_DATA)
        self.policy.data_categories = [DataCategory.USAGE_DATA, DataCategory.TECHNICAL_INFO]
        self.policy.retention_period = "Not Specified" # Doesn't matter for this case
        results_no_pii = self.verifier.verify_policy_properties(self.policy, ["retention_limits_defined_for_pii"])
        self.assertTrue(results_no_pii.get("retention_limits_defined_for_pii")) # Trivially true

    def test_clear_contact_for_privacy_inquiries(self):
        # Scenario 1: "contact" keyword present
        self.policy.text_summary = "Please contact us for privacy questions."
        results_contact = self.verifier.verify_policy_properties(self.policy, ["clear_contact_for_privacy_inquiries"])
        self.assertTrue(results_contact.get("clear_contact_for_privacy_inquiries"))

        # Scenario 2: "DPO" keyword present
        self.policy.text_summary = "Reach out to our DPO."
        results_dpo = self.verifier.verify_policy_properties(self.policy, ["clear_contact_for_privacy_inquiries"])
        self.assertTrue(results_dpo.get("clear_contact_for_privacy_inquiries"))

        # Scenario 3: No relevant keywords
        self.policy.text_summary = "We handle your data."
        results_no_keyword = self.verifier.verify_policy_properties(self.policy, ["clear_contact_for_privacy_inquiries"])
        self.assertFalse(results_no_keyword.get("clear_contact_for_privacy_inquiries"))

    def test_unknown_property(self):
        results = self.verifier.verify_policy_properties(self.policy, ["this_property_does_not_exist"])
        # Placeholder verifier defaults to False for unknown properties and prints a warning
        self.assertFalse(results.get("this_property_does_not_exist"))

    def test_multiple_properties(self):
        self.policy.purposes.append(Purpose.MARKETING)
        self.policy.text_summary = "Marketing is done. Opt-out available. Contact our privacy officer."
        self.policy.data_categories = [DataCategory.PERSONAL_INFO]
        self.policy.retention_period = "1 year"

        properties_to_test = [
            "opt_out_possible_for_marketing",
            "retention_limits_defined_for_pii",
            "clear_contact_for_privacy_inquiries"
        ]
        results = self.verifier.verify_policy_properties(self.policy, properties_to_test)
        self.assertTrue(results.get("opt_out_possible_for_marketing"))
        self.assertTrue(results.get("retention_limits_defined_for_pii"))
        self.assertTrue(results.get("clear_contact_for_privacy_inquiries"))
        self.assertEqual(len(results), len(properties_to_test))

if __name__ == '__main__':
    unittest.main()
