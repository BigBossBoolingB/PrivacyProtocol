import unittest
from privacy_protocol_core.policy_evaluator import PolicyEvaluator
from privacy_protocol_core.policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis
from privacy_protocol_core.consent import UserConsent
from privacy_protocol_core.data_attribute import DataAttribute, SensitivityLevel

class TestPolicyEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = PolicyEvaluator()

        # Shared Policy for most tests
        self.policy1 = PrivacyPolicy(
            policy_id="eval_policy1", version="1.0",
            data_categories=[
                DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA,
                DataCategory.TECHNICAL_INFO, DataCategory.LOCATION_DATA
            ],
            purposes=[
                Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS,
                Purpose.MARKETING, Purpose.SECURITY
            ],
            legal_basis=[LegalBasis.CONSENT, LegalBasis.CONTRACT],
            third_parties_shared_with=["AnalyticsCorp", "MarketingPartner"]
        )

        # Shared Data Attributes
        self.email_attr = DataAttribute(attribute_name="email", category=DataCategory.PERSONAL_INFO)
        self.ip_attr = DataAttribute(attribute_name="ip", category=DataCategory.TECHNICAL_INFO)
        self.click_attr = DataAttribute(attribute_name="click", category=DataCategory.USAGE_DATA)
        self.gps_attr = DataAttribute(attribute_name="gps", category=DataCategory.LOCATION_DATA)
        self.biometric_attr = DataAttribute(attribute_name="fingerprint", category=DataCategory.BIOMETRIC_DATA) # Not in policy1

        # Shared Consents
        self.full_consent_user1 = UserConsent(
            user_id="user1", policy_id=self.policy1.policy_id, policy_version="1.0",
            data_categories_consented=[
                DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA,
                DataCategory.TECHNICAL_INFO, DataCategory.LOCATION_DATA
            ],
            purposes_consented=[
                Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS, Purpose.MARKETING
            ],
            third_parties_consented=["AnalyticsCorp", "MarketingPartner", "*"] # Wildcard included
        )
        self.limited_consent_user2 = UserConsent(
            user_id="user2", policy_id=self.policy1.policy_id, policy_version="1.0",
            data_categories_consented=[DataCategory.PERSONAL_INFO],
            purposes_consented=[Purpose.SERVICE_DELIVERY],
            third_parties_consented=[] # No third parties
        )
        self.inactive_consent_user3 = UserConsent(
            user_id="user3", policy_id=self.policy1.policy_id, policy_version="1.0",
            data_categories_consented=[DataCategory.PERSONAL_INFO],
            purposes_consented=[Purpose.SERVICE_DELIVERY],
            is_active=False
        )

    def test_operation_fully_permitted(self):
        # Use email (PERSONAL_INFO) for MARKETING with MarketingPartner
        attrs = [self.email_attr]
        purpose = Purpose.MARKETING
        third_party = "MarketingPartner"
        self.assertTrue(
            self.evaluator.is_operation_permitted(self.policy1, self.full_consent_user1, attrs, purpose, third_party),
            "Should be permitted: email for marketing with partner, full consent."
        )

    def test_permitted_no_third_party_needed(self):
        attrs = [self.email_attr, self.click_attr] # PERSONAL_INFO, USAGE_DATA
        purpose = Purpose.ANALYTICS # User1 consented
        self.assertTrue(
            self.evaluator.is_operation_permitted(self.policy1, self.full_consent_user1, attrs, purpose, None),
            "Should be permitted: analytics on email/clicks, no TP, full consent."
        )

    def test_permitted_wildcard_third_party(self):
        attrs = [self.ip_attr] # TECHNICAL_INFO
        purpose = Purpose.ANALYTICS # User1 consented
        third_party = "NewAnalyticsCorp" # Not explicitly listed, but full_consent_user1 has wildcard
        self.assertTrue(
            self.evaluator.is_operation_permitted(self.policy1, self.full_consent_user1, attrs, purpose, third_party),
            "Should be permitted due to wildcard third-party consent."
        )

    def test_denied_purpose_not_in_policy(self):
        attrs = [self.email_attr]
        purpose = Purpose.RESEARCH_DEVELOPMENT # Not in self.policy1.purposes
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.full_consent_user1, attrs, purpose),
            "Should be denied: purpose not in policy."
        )

    def test_denied_category_not_in_policy(self):
        attrs = [self.biometric_attr] # BIOMETRIC_DATA not in self.policy1.data_categories
        purpose = Purpose.SERVICE_DELIVERY
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.full_consent_user1, attrs, purpose),
            "Should be denied: data category not in policy."
        )

    def test_denied_no_consent_object(self):
        attrs = [self.email_attr]
        purpose = Purpose.SERVICE_DELIVERY
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, None, attrs, purpose),
            "Should be denied: no consent object provided."
        )

    def test_denied_inactive_consent(self):
        attrs = [self.email_attr]
        purpose = Purpose.SERVICE_DELIVERY
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.inactive_consent_user3, attrs, purpose),
            "Should be denied: consent is inactive."
        )

    def test_denied_category_not_in_consent(self):
        attrs = [self.gps_attr] # LOCATION_DATA, user2 only consented to PERSONAL_INFO
        purpose = Purpose.SERVICE_DELIVERY
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.limited_consent_user2, attrs, purpose),
            "Should be denied: data category not in user's consent."
        )

    def test_denied_purpose_not_in_consent(self):
        attrs = [self.email_attr] # PERSONAL_INFO consented by user2
        purpose = Purpose.MARKETING # User2 only consented to SERVICE_DELIVERY
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.limited_consent_user2, attrs, purpose),
            "Should be denied: purpose not in user's consent."
        )

    def test_denied_third_party_not_in_consent(self):
        attrs = [self.email_attr] # PERSONAL_INFO consented by user2 for SERVICE_DELIVERY
        purpose = Purpose.SERVICE_DELIVERY # Consented by user2
        third_party = "AnalyticsCorp" # User2 has empty third_parties_consented
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.limited_consent_user2, attrs, purpose, third_party),
            "Should be denied: third party not in user's consent (and no wildcard)."
        )

    def test_permitted_operation_multiple_attributes(self):
        # All attributes and purpose are covered by policy and full_consent_user1
        attrs = [self.email_attr, self.ip_attr, self.click_attr]
        purpose = Purpose.ANALYTICS
        third_party = "AnalyticsCorp"
        self.assertTrue(
            self.evaluator.is_operation_permitted(self.policy1, self.full_consent_user1, attrs, purpose, third_party),
            "Should be permitted with multiple attributes fully consented."
        )

    def test_denied_one_of_multiple_attributes_not_consented_category(self):
        # User2 consents to PERSONAL_INFO (email_attr) but not USAGE_DATA (click_attr)
        attrs = [self.email_attr, self.click_attr]
        purpose = Purpose.SERVICE_DELIVERY # User2 consents to this purpose
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.limited_consent_user2, attrs, purpose),
            "Should be denied if one attribute's category is not consented."
        )

    def test_invalid_inputs_return_false(self):
        # Test that invalid input types result in False, not crashes (as per current implementation)
        self.assertFalse(
            self.evaluator.is_operation_permitted("not_a_policy", self.full_consent_user1, [self.email_attr], Purpose.SERVICE_DELIVERY),
            "Should return False for invalid policy type."
        )
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, "not_consent", [self.email_attr], Purpose.SERVICE_DELIVERY),
            "Should return False for invalid consent type."
        )
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.full_consent_user1, "not_a_list_of_attributes", Purpose.SERVICE_DELIVERY),
            "Should return False for invalid data_attributes type."
        )
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.full_consent_user1, [self.email_attr, "not_an_attribute_object"], Purpose.SERVICE_DELIVERY),
            "Should return False if list contains non-DataAttribute."
        )
        self.assertFalse(
            self.evaluator.is_operation_permitted(self.policy1, self.full_consent_user1, [self.email_attr], "not_a_purpose_enum"),
            "Should return False for invalid purpose type."
        )

if __name__ == '__main__':
    unittest.main()
