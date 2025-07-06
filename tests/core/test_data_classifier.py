import unittest
from privacy_protocol_core.data_classifier import DataClassifier
from privacy_protocol_core.data_attribute import DataAttribute, DataCategory, SensitivityLevel

class TestDataClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier_no_registry = DataClassifier()

        self.pre_registered_attr = DataAttribute(
            attribute_name="user_custom_id",
            category=DataCategory.PERSONAL_INFO,
            sensitivity_level=SensitivityLevel.HIGH
        )
        self.registry = {"user_custom_id": self.pre_registered_attr}
        self.classifier_with_registry = DataClassifier(attribute_registry=self.registry)

    def test_classify_empty_dict(self):
        classified = self.classifier_no_registry.classify_data({})
        self.assertEqual(classified, [])

    def test_classify_known_patterns(self):
        data = {
            "email": "test@example.com",
            "user_ip_address": "127.0.0.1",
            "full_name": "John Doe",
            "cc_num": "4111...",
            "user_query": "how to bake a cake"
        }
        classified = self.classifier_no_registry.classify_data(data)

        expected_classifications = {
            "email": ("email_address", DataCategory.PERSONAL_INFO, SensitivityLevel.MEDIUM),
            "user_ip_address": ("ip_address", DataCategory.TECHNICAL_INFO, SensitivityLevel.MEDIUM),
            "full_name": ("full_name", DataCategory.PERSONAL_INFO, SensitivityLevel.HIGH),
            "cc_num": ("credit_card_number", DataCategory.FINANCIAL_INFO, SensitivityLevel.CRITICAL),
            "user_query": ("search_query", DataCategory.USAGE_DATA, SensitivityLevel.MEDIUM)
        }

        self.assertEqual(len(classified), len(data))
        for original_key, attr_obj in classified:
            self.assertIn(original_key, expected_classifications)
            if attr_obj:
                expected_name, expected_cat, expected_sens = expected_classifications[original_key]
                self.assertEqual(attr_obj.attribute_name, expected_name)
                self.assertEqual(attr_obj.category, expected_cat)
                self.assertEqual(attr_obj.sensitivity_level, expected_sens)
            else:
                self.fail(f"Attribute for key '{original_key}' should not be None")

    def test_classify_unknown_pattern_fallback(self):
        data = {"completely_new_field_type": "some value"}
        classified = self.classifier_no_registry.classify_data(data)

        self.assertEqual(len(classified), 1)
        original_key, attr_obj = classified[0]
        self.assertEqual(original_key, "completely_new_field_type")
        self.assertIsNotNone(attr_obj)
        self.assertEqual(attr_obj.attribute_name, "completely_new_field_type") # Falls back to key name
        self.assertEqual(attr_obj.category, DataCategory.OTHER) # Default fallback category
        self.assertEqual(attr_obj.sensitivity_level, SensitivityLevel.LOW) # Default fallback sensitivity

    def test_classify_with_attribute_registry_hit(self):
        data = {"user_custom_id": "custom123", "email": "test@example.com"}
        classified = self.classifier_with_registry.classify_data(data)

        found_custom = False
        found_email = False
        for original_key, attr_obj in classified:
            if original_key == "user_custom_id":
                self.assertIsNotNone(attr_obj)
                # It should return the *instance* from the registry
                self.assertIs(attr_obj, self.pre_registered_attr, "Should return the exact object from registry.")
                found_custom = True
            elif original_key == "email":
                 self.assertIsNotNone(attr_obj)
                 self.assertEqual(attr_obj.attribute_name, "email_address")
                 found_email = True
        self.assertTrue(found_custom, "Pre-registered attribute was not found or not used.")
        self.assertTrue(found_email, "Rule-based attribute (email) was not classified.")

    def test_classify_with_attribute_registry_miss_then_rule(self):
        # Registry has "user_custom_id", data has "normal_ip_address" which should be rule-based
        data = {"normal_ip_address": "1.2.3.4"}
        classified = self.classifier_with_registry.classify_data(data)

        self.assertEqual(len(classified), 1)
        original_key, attr_obj = classified[0]
        self.assertEqual(original_key, "normal_ip_address")
        self.assertIsNotNone(attr_obj)
        self.assertEqual(attr_obj.attribute_name, "ip_address") # From rule
        self.assertEqual(attr_obj.category, DataCategory.TECHNICAL_INFO)

    def test_classify_case_insensitivity_of_keys(self):
        data = {"EMAIL": "ignorecase@example.com", "Ip_AdDrEsS": "1.1.1.1"}
        classified = self.classifier_no_registry.classify_data(data)

        email_classified = False
        ip_classified = False
        for original_key, attr_obj in classified:
            if original_key == "EMAIL" and attr_obj:
                self.assertEqual(attr_obj.attribute_name, "email_address")
                self.assertEqual(attr_obj.category, DataCategory.PERSONAL_INFO)
                email_classified = True
            elif original_key == "Ip_AdDrEsS" and attr_obj:
                self.assertEqual(attr_obj.attribute_name, "ip_address")
                self.assertEqual(attr_obj.category, DataCategory.TECHNICAL_INFO)
                ip_classified = True
        self.assertTrue(email_classified, "Case-insensitive email key not classified correctly.")
        self.assertTrue(ip_classified, "Case-insensitive IP key not classified correctly.")

    def test_input_not_dictionary(self):
        with self.assertRaisesRegex(ValueError, "Input data must be a dictionary."):
            self.classifier_no_registry.classify_data("not a dict")
        with self.assertRaisesRegex(ValueError, "Input data must be a dictionary."):
            self.classifier_no_registry.classify_data(["a", "list"])

if __name__ == '__main__':
    unittest.main()
