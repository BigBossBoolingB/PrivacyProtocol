import unittest
import json
from privacy_protocol_core.data_attribute import DataAttribute, DataCategory, SensitivityLevel, ObfuscationMethod

class TestDataAttribute(unittest.TestCase):

    def test_attribute_instantiation_defaults(self):
        attr = DataAttribute(attribute_name="test_attr", category=DataCategory.OTHER)
        self.assertIsNotNone(attr.attribute_id)
        self.assertEqual(attr.attribute_name, "test_attr")
        self.assertEqual(attr.category, DataCategory.OTHER)
        self.assertEqual(attr.sensitivity_level, SensitivityLevel.MEDIUM) # Default
        self.assertTrue(attr.is_pii) # Default for MEDIUM sensitivity
        self.assertEqual(attr.obfuscation_method_preferred, ObfuscationMethod.NONE) # Default
        self.assertEqual(attr.description, "")

    def test_attribute_instantiation_with_values(self):
        attr = DataAttribute(
            attribute_id="attr_id_1",
            attribute_name="user_ip_address",
            category=DataCategory.TECHNICAL_INFO,
            sensitivity_level=SensitivityLevel.HIGH,
            is_pii=True, # Explicitly set
            obfuscation_method_preferred=ObfuscationMethod.REDACT,
            description="User's last known IP address."
        )
        self.assertEqual(attr.attribute_id, "attr_id_1")
        self.assertEqual(attr.attribute_name, "user_ip_address")
        self.assertEqual(attr.category, DataCategory.TECHNICAL_INFO)
        self.assertEqual(attr.sensitivity_level, SensitivityLevel.HIGH)
        self.assertTrue(attr.is_pii)
        self.assertEqual(attr.obfuscation_method_preferred, ObfuscationMethod.REDACT)
        self.assertEqual(attr.description, "User's last known IP address.")

    def test_is_pii_auto_determination(self):
        attr_low = DataAttribute(attribute_name="pref1", category=DataCategory.USAGE_DATA, sensitivity_level=SensitivityLevel.LOW)
        self.assertFalse(attr_low.is_pii)

        attr_medium = DataAttribute(attribute_name="email1", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM)
        self.assertTrue(attr_medium.is_pii)

        attr_high = DataAttribute(attribute_name="ssn1", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.HIGH)
        self.assertTrue(attr_high.is_pii)

        attr_critical = DataAttribute(attribute_name="biometric1", category=DataCategory.BIOMETRIC_DATA, sensitivity_level=SensitivityLevel.CRITICAL)
        self.assertTrue(attr_critical.is_pii)

        attr_explicit_false_pii = DataAttribute(attribute_name="id_anon", category=DataCategory.TECHNICAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM, is_pii=False)
        self.assertFalse(attr_explicit_false_pii.is_pii)

    def test_to_dict(self):
        attr = DataAttribute(attribute_name="dict_attr", category=DataCategory.FINANCIAL_INFO, sensitivity_level=SensitivityLevel.CRITICAL)
        attr_dict = attr.to_dict()

        self.assertEqual(attr_dict["attribute_id"], attr.attribute_id)
        self.assertEqual(attr_dict["attribute_name"], "dict_attr")
        self.assertEqual(attr_dict["category"], DataCategory.FINANCIAL_INFO.value)
        self.assertEqual(attr_dict["sensitivity_level"], SensitivityLevel.CRITICAL.value)
        self.assertTrue(attr_dict["is_pii"])
        self.assertEqual(attr_dict["obfuscation_method_preferred"], ObfuscationMethod.NONE.value)

    def test_to_json(self):
        attr = DataAttribute(attribute_name="json_attr", category=DataCategory.LOCATION_DATA, description="test json")
        attr_json = attr.to_json()
        attr_data_from_json = json.loads(attr_json)

        self.assertEqual(attr_data_from_json["attribute_id"], attr.attribute_id)
        self.assertEqual(attr_data_from_json["description"], "test json")
        self.assertEqual(attr_data_from_json["category"], DataCategory.LOCATION_DATA.value)


    def test_from_dict(self):
        attr_data = {
            "attribute_id": "dict_attr_id",
            "attribute_name": "loaded_attr",
            "category": DataCategory.HEALTH_INFO.value,
            "sensitivity_level": SensitivityLevel.HIGH.value,
            "is_pii": True, # Explicit
            "obfuscation_method_preferred": ObfuscationMethod.ENCRYPT.value,
            "description": "Loaded from dict."
        }
        attr = DataAttribute.from_dict(attr_data)

        self.assertEqual(attr.attribute_id, "dict_attr_id")
        self.assertEqual(attr.attribute_name, "loaded_attr")
        self.assertEqual(attr.category, DataCategory.HEALTH_INFO)
        self.assertEqual(attr.sensitivity_level, SensitivityLevel.HIGH)
        self.assertTrue(attr.is_pii)
        self.assertEqual(attr.obfuscation_method_preferred, ObfuscationMethod.ENCRYPT)
        self.assertEqual(attr.description, "Loaded from dict.")

    def test_from_dict_invalid_enums(self):
        attr_data = {
            "attribute_name": "invalid_enum_attr",
            "category": "NonExistentCategory",
            "sensitivity_level": "NonExistentSensitivity",
            "obfuscation_method_preferred": "NonExistentMethod"
        }
        attr = DataAttribute.from_dict(attr_data)
        self.assertIsNone(attr.category)
        self.assertEqual(attr.sensitivity_level, SensitivityLevel.MEDIUM) # Defaults
        self.assertEqual(attr.obfuscation_method_preferred, ObfuscationMethod.NONE) # Defaults


    def test_from_json(self):
        attr_data = {
            "attribute_name": "json_loaded_attr",
            "category": DataCategory.USAGE_DATA.value,
            "sensitivity_level": SensitivityLevel.LOW.value
        }
        attr_json = json.dumps(attr_data)
        attr = DataAttribute.from_json(attr_json)

        self.assertEqual(attr.attribute_name, "json_loaded_attr")
        self.assertEqual(attr.category, DataCategory.USAGE_DATA)
        self.assertEqual(attr.sensitivity_level, SensitivityLevel.LOW)
        self.assertFalse(attr.is_pii) # Auto-calculated based on LOW sensitivity

    def test_invalid_enum_type_at_instantiation(self):
        with self.assertRaisesRegex(ValueError, "category must be an instance of DataCategory enum"):
            DataAttribute(attribute_name="test", category="NotAnEnumObject")

        with self.assertRaisesRegex(ValueError, "sensitivity_level must be an instance of SensitivityLevel enum"):
            DataAttribute(attribute_name="test", category=DataCategory.OTHER, sensitivity_level="NotAnEnumObject")

        with self.assertRaisesRegex(ValueError, "obfuscation_method_preferred must be an instance of ObfuscationMethod enum"):
            DataAttribute(attribute_name="test", category=DataCategory.OTHER, obfuscation_method_preferred="NotAnEnumObject")

    def test_repr(self):
        attr = DataAttribute(attribute_name="repr_attr", category=DataCategory.PERSONAL_INFO, is_pii=True)
        self.assertEqual(repr(attr), "<DataAttribute(name='repr_attr', category='Personal_Info', pii=True)>")

if __name__ == '__main__':
    unittest.main()
