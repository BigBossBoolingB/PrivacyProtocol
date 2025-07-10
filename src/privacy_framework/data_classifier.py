# src/privacy_framework/data_classifier.py
"""
Classifies raw data into DataAttribute objects.
"""
import re
from typing import List, Dict, Any, Optional

try:
    from .data_attribute import DataAttribute, DataCategory, SensitivityLevel, ObfuscationMethod
except ImportError:
    # Fallback for direct execution or different project structures
    from privacy_framework.data_attribute import DataAttribute, DataCategory, SensitivityLevel, ObfuscationMethod

class DataClassifier:
    """
    Classifies raw data fields into DataAttribute objects using rule-based methods.
    """

    # Simple regex for email (not exhaustive, but good for demo)
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    # Simple regex for North American phone numbers (very basic)
    PHONE_REGEX = r"^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$"

    def classify_data_item(self, value: Any, key_hint: Optional[str] = None) -> DataAttribute:
        """
        Classifies a single data item (value) into a DataAttribute.
        Uses key_hint if the value comes from a dictionary.
        """
        # attr_name will be determined based on context or specific detection.
        # category, sensitivity, is_pii, obfuscation_pref will be set by rules.

        _attr_name_from_detection = None # Canonical name if detected by value
        category = DataCategory.OTHER
        sensitivity = SensitivityLevel.LOW
        is_pii = False
        obfuscation_pref = ObfuscationMethod.NONE # Default, can be overridden by specific rules

        if isinstance(value, str):
            # Email
            if re.match(self.EMAIL_REGEX, value):
                _attr_name_from_detection = "email_address"
                category = DataCategory.PERSONAL_INFO
                sensitivity = SensitivityLevel.CRITICAL
                is_pii = True
                obfuscation_pref = ObfuscationMethod.HASH
            elif key_hint and "email" in key_hint.lower(): # Key hint suggests email
                category = DataCategory.PERSONAL_INFO
                sensitivity = SensitivityLevel.CRITICAL
                is_pii = True
                obfuscation_pref = ObfuscationMethod.HASH
            # Phone Number
            elif re.match(self.PHONE_REGEX, value):
                _attr_name_from_detection = "phone_number"
                category = DataCategory.PERSONAL_INFO
                sensitivity = SensitivityLevel.CRITICAL
                is_pii = True
                obfuscation_pref = ObfuscationMethod.MASK
            elif key_hint and ("phone" in key_hint.lower() or "contact_no" in key_hint.lower()):
                category = DataCategory.PERSONAL_INFO
                sensitivity = SensitivityLevel.CRITICAL
                is_pii = True
                obfuscation_pref = ObfuscationMethod.MASK
            # IP Address based on key_hint (value check is more complex)
            elif key_hint and ("ip_address" in key_hint.lower() or "ipaddress" in key_hint.lower()):
                # attr_name will be key_hint
                category = DataCategory.DEVICE_INFO
                sensitivity = SensitivityLevel.MEDIUM
            # Device ID based on key_hint
            elif key_hint and ("deviceid" in key_hint.lower() or "device_id" in key_hint.lower()):
                # attr_name will be key_hint
                category = DataCategory.DEVICE_INFO
                sensitivity = SensitivityLevel.MEDIUM
            # Name (heuristic based on key_hint, value could be anything)
            elif key_hint and ("name" in key_hint.lower() or "firstname" in key_hint.lower() or "lastname" in key_hint.lower()):
                # attr_name will be key_hint
                category = DataCategory.PERSONAL_INFO
                sensitivity = SensitivityLevel.CRITICAL
                is_pii = True
                obfuscation_pref = ObfuscationMethod.REDACT
            # Location based on key_hint
            elif key_hint and ("location" in key_hint.lower() or "address" in key_hint.lower() or \
                               "city" in key_hint.lower() or "zip" in key_hint.lower() or "postcode" in key_hint.lower()):
                # attr_name will be key_hint
                category = DataCategory.LOCATION_DATA
                sensitivity = SensitivityLevel.HIGH
                obfuscation_pref = ObfuscationMethod.MASK
            # IP Address based on key_hint (value check is more complex)
            elif key_hint and ("ip_address" in key_hint.lower() or "ipaddress" in key_hint.lower()):
                # attr_name will be key_hint
                category = DataCategory.DEVICE_INFO
                sensitivity = SensitivityLevel.MEDIUM
            # Device ID based on key_hint
            elif key_hint and ("deviceid" in key_hint.lower() or "device_id" in key_hint.lower()):
                # attr_name will be key_hint
                category = DataCategory.DEVICE_INFO
                sensitivity = SensitivityLevel.MEDIUM
            # Default for other strings if a key_hint was given
            elif key_hint and key_hint != "data_item": # Avoid setting category if only "data_item" hint
                category = DataCategory.OTHER
                sensitivity = SensitivityLevel.LOW
            # If it's a generic string value without a good key_hint, _attr_name_from_detection is None.
            # It will be handled by final_attr_name logic.

        elif isinstance(value, (int, float)):
            # _attr_name_from_detection remains None for numbers unless a specific rule sets it
            if key_hint and ("age" in key_hint.lower()):
                category = DataCategory.PERSONAL_INFO
                sensitivity = SensitivityLevel.MEDIUM
                is_pii = True # Often considered PII
            elif key_hint and ("amount" in key_hint.lower() or "price" in key_hint.lower() or "salary" in key_hint.lower()):
                category = DataCategory.FINANCIAL_DATA
                sensitivity = SensitivityLevel.HIGH
            else:
                category = DataCategory.USAGE_DATA # Or OTHER if not clearly usage
                sensitivity = SensitivityLevel.LOW

        # Determine final attribute name
        if _attr_name_from_detection and (not key_hint or key_hint == "data_item"):
            # If value-based detection gave a name (email, phone) & no specific key_hint (or generic one)
            final_attr_name = _attr_name_from_detection
        elif key_hint:
            final_attr_name = key_hint
        elif _attr_name_from_detection: # No key_hint, but value was detected (e.g. direct string "user@ex.com")
            final_attr_name = _attr_name_from_detection
        else:
            final_attr_name = "unknown_field"

        # Add more rules for other types (bool, lists, nested dicts) as needed

        return DataAttribute(
            attribute_name=final_attr_name,
            category=category,
            sensitivity_level=sensitivity,
            is_pii=is_pii,
            obfuscation_method_preferred=obfuscation_pref
        )

    def classify_data(self, data: Any, parent_key: Optional[str] = None) -> List[DataAttribute]:
        """
        Classifies raw data, which can be a dictionary or a single value,
        into a list of DataAttribute objects.
        Recursively handles nested dictionaries.

        Args:
            data (Any): The raw data to classify (e.g., dict, str, int).
            parent_key (Optional[str]): Used for hierarchical naming of attributes from nested dicts.

        Returns:
            List[DataAttribute]: A list of DataAttribute objects representing the classified data.
        """
        attributes: List[DataAttribute] = []

        if isinstance(data, dict):
            for key, value in data.items():
                full_key_hint = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, dict): # Nested dictionary
                    attributes.extend(self.classify_data(value, parent_key=full_key_hint))
                elif isinstance(value, list): # List of items
                    for i, item in enumerate(value):
                        item_key_hint = f"{full_key_hint}[{i}]"
                        # If list items are complex (dicts), recurse, else classify item directly
                        if isinstance(item, dict):
                             attributes.extend(self.classify_data(item, parent_key=item_key_hint))
                        else:
                            attributes.append(self.classify_data_item(item, key_hint=item_key_hint))
                else: # Simple value
                    attributes.append(self.classify_data_item(value, key_hint=full_key_hint))
        else: # Single value not in a dictionary (e.g. just a string or number)
            attributes.append(self.classify_data_item(data, key_hint=parent_key or "data_item"))

        return attributes

if __name__ == '__main__':
    classifier = DataClassifier()

    print("--- Classifying Single String Values ---")
    email_str = "test.user@example.com"
    attr_email_str = classifier.classify_data(email_str)
    print(f"Data: '{email_str}' -> Classified: {attr_email_str[0]}")

    phone_str = " (123) 456-7890 "
    attr_phone_str = classifier.classify_data(phone_str)
    print(f"Data: '{phone_str}' -> Classified: {attr_phone_str[0]}")

    generic_str = "Hello world"
    attr_generic_str = classifier.classify_data(generic_str)
    print(f"Data: '{generic_str}' -> Classified: {attr_generic_str[0]}")

    print("\n--- Classifying Dictionary Data ---")
    user_profile_data = {
        "username": "jdoe",
        "personalInfo": {
            "firstName": "John",
            "lastName": "Doe",
            "email_address": "john.doe@work.com",
            "age": 30
        },
        "contactPreferences": {
            "marketingOptIn": True,
            "primary_phone": "555-123-4567"
        },
        "session": {
            "last_login_ip": "192.168.1.100",
            "device_id_used": "deviceABC123"
        },
        "notes": "A regular customer."
    }

    classified_profile_attrs = classifier.classify_data(user_profile_data)
    print("Classified attributes from user_profile_data:")
    for attr in classified_profile_attrs:
        print(f"  - {attr.attribute_name}: Category={attr.category.name}, Sensitivity={attr.sensitivity_level.name}, PII={attr.is_pii}, ObfPref={attr.obfuscation_method_preferred.name}")

    print("\n--- Classifying Data with a List ---")
    data_with_list = {
        "order_id": "ORD123",
        "items": [
            {"name": "Product A", "price": 10.99},
            {"name": "Service B", "price": 25.00}
        ],
        "shipping_address": "123 Main St, Anytown, USA"
    }
    classified_list_attrs = classifier.classify_data(data_with_list)
    print("Classified attributes from data_with_list:")
    for attr in classified_list_attrs:
        print(f"  - {attr.attribute_name}: Category={attr.category.name}, Sensitivity={attr.sensitivity_level.name}")
