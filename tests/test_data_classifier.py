# tests/test_data_classifier.py
import unittest

# Adjust import path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.data_classifier import DataClassifier
from src.privacy_framework.data_attribute import DataCategory, SensitivityLevel, ObfuscationMethod

class TestDataClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = DataClassifier()

    def test_classify_email_string(self):
        email = "user@example.com"
        attrs = self.classifier.classify_data(email)
        self.assertEqual(len(attrs), 1)
        attr = attrs[0]
        self.assertEqual(attr.attribute_name, "email_address")
        self.assertEqual(attr.category, DataCategory.PERSONAL_INFO)
        self.assertEqual(attr.sensitivity_level, SensitivityLevel.CRITICAL)
        self.assertTrue(attr.is_pii)
        self.assertIn(attr.obfuscation_method_preferred, [ObfuscationMethod.HASH, ObfuscationMethod.MASK])

    def test_classify_phone_string(self):
        phone = "123-456-7890"
        attrs = self.classifier.classify_data(phone)
        self.assertEqual(len(attrs), 1)
        attr = attrs[0]
        self.assertEqual(attr.attribute_name, "phone_number")
        self.assertEqual(attr.category, DataCategory.PERSONAL_INFO)
        self.assertEqual(attr.sensitivity_level, SensitivityLevel.CRITICAL)
        self.assertTrue(attr.is_pii)
        self.assertEqual(attr.obfuscation_method_preferred, ObfuscationMethod.MASK)

    def test_classify_generic_string(self):
        text = "Some generic text"
        attrs = self.classifier.classify_data(text)
        self.assertEqual(len(attrs), 1)
        attr = attrs[0]
        self.assertEqual(attr.attribute_name, "data_item") # Default name for single unkeyed item
        self.assertEqual(attr.category, DataCategory.OTHER)
        self.assertEqual(attr.sensitivity_level, SensitivityLevel.LOW)
        self.assertFalse(attr.is_pii)

    def test_classify_dictionary_simple(self):
        data = {
            "email": "test@host.com",
            "user_name": "jdoe",
            "ip_address": "192.168.0.1",
            "age": 30,
            "comment": "This is a comment."
        }
        attrs = self.classifier.classify_data(data)

        attr_map = {a.attribute_name: a for a in attrs}
        self.assertEqual(len(attrs), 5)

        self.assertEqual(attr_map["email"].category, DataCategory.PERSONAL_INFO)
        self.assertTrue(attr_map["email"].is_pii)

        self.assertEqual(attr_map["user_name"].category, DataCategory.PERSONAL_INFO) # "name" in key_hint
        self.assertTrue(attr_map["user_name"].is_pii)

        self.assertEqual(attr_map["ip_address"].category, DataCategory.DEVICE_INFO)
        self.assertEqual(attr_map["ip_address"].sensitivity_level, SensitivityLevel.MEDIUM)

        self.assertEqual(attr_map["age"].category, DataCategory.PERSONAL_INFO)
        self.assertTrue(attr_map["age"].is_pii)

        self.assertEqual(attr_map["comment"].category, DataCategory.OTHER)
        self.assertEqual(attr_map["comment"].sensitivity_level, SensitivityLevel.LOW)


    def test_classify_nested_dictionary(self):
        data = {
            "user": {
                "id": 123,
                "details": {
                    "email": "nested@example.com",
                    "address": "123 Privacy Lane"
                }
            },
            "transaction_id": "txn_abc"
        }
        attrs = self.classifier.classify_data(data)
        attr_map = {a.attribute_name: a for a in attrs}

        self.assertTrue("user.details.email" in attr_map)
        self.assertEqual(attr_map["user.details.email"].category, DataCategory.PERSONAL_INFO)

        self.assertTrue("user.details.address" in attr_map)
        self.assertEqual(attr_map["user.details.address"].category, DataCategory.LOCATION_DATA)

        self.assertTrue("user.id" in attr_map) # Classified as numeric, likely USAGE_DATA or OTHER
        self.assertEqual(attr_map["user.id"].category, DataCategory.USAGE_DATA)


    def test_classify_list_of_simple_values(self):
        data = {"tags": ["urgent", "customer_feedback", "pii_related"]}
        attrs = self.classifier.classify_data(data)
        attr_map = {a.attribute_name: a for a in attrs}

        self.assertTrue("tags[0]" in attr_map)
        self.assertEqual(attr_map["tags[0]"].category, DataCategory.OTHER) # Default for strings in list
        self.assertEqual(attr_map["tags[0]"].attribute_name, "tags[0]")

    def test_classify_list_of_dictionaries(self):
        data = {
            "contacts": [
                {"type": "email", "value": "primary@example.com"},
                {"type": "phone", "value": "555-000-1111"}
            ]
        }
        attrs = self.classifier.classify_data(data)
        attr_map = {a.attribute_name: a for a in attrs}

        # Example check, names will be like "contacts[0].type", "contacts[0].value"
        self.assertTrue("contacts[0].value" in attr_map)
        email_attr = attr_map["contacts[0].value"]
        # The value "primary@example.com" should make it PERSONAL_INFO
        # However, the current classify_data_item uses key_hint primarily for dicts.
        # For list items, the key_hint is "contacts[0].value", which doesn't say "email".
        # This highlights a limitation: content-based classification for list items needs enhancement.
        # For now, it might classify based on the string content itself.
        self.assertEqual(email_attr.category, DataCategory.PERSONAL_INFO)
        self.assertTrue(email_attr.is_pii)


        self.assertTrue("contacts[1].value" in attr_map)
        phone_attr = attr_map["contacts[1].value"]
        self.assertEqual(phone_attr.category, DataCategory.PERSONAL_INFO) # Phone regex should catch this
        self.assertTrue(phone_attr.is_pii)


    def test_key_hint_priority(self):
        # Value looks like generic text, but key_hint suggests email
        data_with_hint = {"user_email_field": "this is actually an address"}
        attrs_hint = self.classifier.classify_data(data_with_hint)
        self.assertEqual(attrs_hint[0].attribute_name, "user_email_field")
        self.assertEqual(attrs_hint[0].category, DataCategory.PERSONAL_INFO) # Due to "email" in key_hint
        self.assertTrue(attrs_hint[0].is_pii)

        # Value is clearly an email, key_hint is generic
        data_no_hint = {"generic_field": "definitely.an.email@example.net"}
        attrs_no_hint = self.classifier.classify_data(data_no_hint)
        self.assertEqual(attrs_no_hint[0].attribute_name, "generic_field")
        self.assertEqual(attrs_no_hint[0].category, DataCategory.PERSONAL_INFO) # Due to regex match on value
        self.assertTrue(attrs_no_hint[0].is_pii)

if __name__ == '__main__':
    unittest.main()
