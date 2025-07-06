import re
try:
    from .data_attribute import DataAttribute, DataCategory, SensitivityLevel
except ImportError: # For standalone testing
    from data_attribute import DataAttribute, DataCategory, SensitivityLevel

class DataClassifier:
    def __init__(self, attribute_registry=None):
        """
        Initializes the DataClassifier.
        Args:
            attribute_registry (dict, optional): A pre-populated registry of
                                                 attribute_name -> DataAttribute object.
                                                 If None, attributes will be created on the fly.
        """
        self.attribute_registry = attribute_registry if attribute_registry else {}
        # Define basic rules for classification.
        # Rules are tuples: (regex_pattern_for_key, DataCategory, SensitivityLevel, attribute_name_format_if_different)
        # More specific rules should come first.
        self.classification_rules = [
            (re.compile(r"email(_address)?$", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.MEDIUM, "email_address"),
            (re.compile(r"ip(_address)?$", re.IGNORECASE), DataCategory.TECHNICAL_INFO, SensitivityLevel.MEDIUM, "ip_address"),
            (re.compile(r"phone(_number)?$", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.MEDIUM, "phone_number"),
            (re.compile(r"address|street", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.HIGH, "physical_address"),
            (re.compile(r"city", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.MEDIUM, "city"),
            (re.compile(r"zip(_code)?|postal(_code)?", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.MEDIUM, "postal_code"),
            (re.compile(r"country", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.MEDIUM, "country"),
            (re.compile(r"name$", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.HIGH, "full_name"), # Matches 'full_name', 'last_name'
            (re.compile(r"first_name$", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.HIGH, "first_name"),
            (re.compile(r"last_name$", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.HIGH, "last_name"),
            (re.compile(r"user(name)?_id$", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.MEDIUM, "user_id"), # Often PII
            (re.compile(r"password|pwd$", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, "password"),
            (re.compile(r"ssn|social_security_number", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, "ssn"),
            (re.compile(r"credit_card|cc_num", re.IGNORECASE), DataCategory.FINANCIAL_INFO, SensitivityLevel.CRITICAL, "credit_card_number"),
            (re.compile(r"cvv|csc", re.IGNORECASE), DataCategory.FINANCIAL_INFO, SensitivityLevel.CRITICAL, "credit_card_cvv"),
            (re.compile(r"bank_account_number", re.IGNORECASE), DataCategory.FINANCIAL_INFO, SensitivityLevel.CRITICAL, "bank_account_number"),
            (re.compile(r"birth_date|dob", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.HIGH, "date_of_birth"),
            (re.compile(r"gender|sex", re.IGNORECASE), DataCategory.PERSONAL_INFO, SensitivityLevel.HIGH, "gender"),
            (re.compile(r"latitude|longitude|gps|location", re.IGNORECASE), DataCategory.LOCATION_DATA, SensitivityLevel.HIGH, "precise_location"),
            (re.compile(r"cookie|session_id", re.IGNORECASE), DataCategory.TECHNICAL_INFO, SensitivityLevel.LOW, "session_identifier"), # Can be medium too
            (re.compile(r"user_agent", re.IGNORECASE), DataCategory.TECHNICAL_INFO, SensitivityLevel.LOW, "user_agent"),
            (re.compile(r"page_view|click_event|interaction|last_page_visited|refer(r)?er", re.IGNORECASE), DataCategory.USAGE_DATA, SensitivityLevel.LOW, "user_interaction_navigation"),
            (re.compile(r"query|search_term", re.IGNORECASE), DataCategory.USAGE_DATA, SensitivityLevel.MEDIUM, "search_query"),
            (re.compile(r"medical_record|health_info", re.IGNORECASE), DataCategory.HEALTH_INFO, SensitivityLevel.CRITICAL, "health_record_identifier"),
            (re.compile(r"fingerprint|face_scan|retina|biometric", re.IGNORECASE), DataCategory.BIOMETRIC_DATA, SensitivityLevel.CRITICAL, "biometric_identifier"),
        ]

    def _get_or_create_attribute(self, name: str, category: DataCategory, sensitivity: SensitivityLevel) -> DataAttribute:
        """
        Retrieves an attribute from the registry or creates a new one if not found.
        This is a simplified version; a real registry might involve more complex lookup or creation logic.
        """
        if name in self.attribute_registry:
            # TODO: Optionally check if category/sensitivity match if pre-registered, or update registry
            return self.attribute_registry[name]

        # Create on the fly if not in registry
        attr = DataAttribute(attribute_name=name, category=category, sensitivity_level=sensitivity)
        # Optionally add to registry if it should be persisted for future use
        # self.attribute_registry[name] = attr
        return attr

    def classify_data(self, data_input: dict) -> list[tuple[str, DataAttribute | None]]:
        """
        Classifies fields in a dictionary input into DataAttribute objects.

        Args:
            data_input: A dictionary where keys are field names and values are the data.

        Returns:
            A list of tuples, where each tuple is (original_key, DataAttribute_object or None).
            Returns None for an attribute if no rule matches and it's not a generic fallback.
        """
        if not isinstance(data_input, dict):
            raise ValueError("Input data must be a dictionary.")

        classified_attributes = []
        for key, value in data_input.items():
            matched_attribute = None
            for pattern, category, sensitivity, attr_name_format in self.classification_rules:
                if pattern.search(key):
                    # Use the specific attribute name format from the rule
                    attribute_name = attr_name_format
                    matched_attribute = self._get_or_create_attribute(attribute_name, category, sensitivity)
                    break

            if matched_attribute:
                classified_attributes.append((key, matched_attribute))
            else:
                # Default/fallback for unkown keys: classify as USAGE_DATA, LOW sensitivity, or OTHER
                # For now, let's make a generic one based on the key itself
                # This could be more sophisticated, e.g. based on value type.
                fallback_attr = self._get_or_create_attribute(key, DataCategory.OTHER, SensitivityLevel.LOW)
                classified_attributes.append((key, fallback_attr))
                # print(f"Warning: No specific classification rule for key '{key}'. Using default.")

        return classified_attributes


if __name__ == '__main__':
    classifier = DataClassifier()

    sample_data_1 = {
        "user_email": "test@example.com",
        "ip": "192.168.1.1",
        "last_login_timestamp": "2023-01-01T10:00:00Z",
        "user_preference_theme": "dark",
        "session_id": "abcdef123456"
    }

    print("--- Classifying Sample Data 1 ---")
    classified1 = classifier.classify_data(sample_data_1)
    for original_key, attr in classified1:
        if attr:
            print(f"Key: '{original_key}' -> Attribute: {attr.attribute_name}, Category: {attr.category.value}, Sensitivity: {attr.sensitivity_level.value}")
        else:
            print(f"Key: '{original_key}' -> No classification")

    # Expected for sample_data_1 (simplified names for this check):
    # user_email -> email_address, PERSONAL_INFO, MEDIUM
    # ip -> ip_address, TECHNICAL_INFO, MEDIUM
    # last_login_timestamp -> last_login_timestamp (OTHER, LOW - default)
    # user_preference_theme -> user_preference_theme (OTHER, LOW - default)
    # session_id -> session_identifier, TECHNICAL_INFO, LOW


    sample_data_2 = {
        "fullName": "Jane Doe",
        "dob": "1990-05-15",
        "user_SocialSecurityNumber": "xxx-xx-xxxx",
        "notes": "Some random text data."
    }
    print("\n--- Classifying Sample Data 2 ---")
    classified2 = classifier.classify_data(sample_data_2)
    for original_key, attr in classified2:
        if attr:
            print(f"Key: '{original_key}' -> Attribute: {attr.attribute_name}, Category: {attr.category.value}, Sensitivity: {attr.sensitivity_level.value}")
        else:
            print(f"Key: '{original_key}' -> No classification")
    # Expected for sample_data_2:
    # fullName -> full_name, PERSONAL_INFO, HIGH
    # dob -> date_of_birth, PERSONAL_INFO, HIGH
    # user_SocialSecurityNumber -> ssn, PERSONAL_INFO, CRITICAL
    # notes -> notes (OTHER, LOW - default)

    # Test with pre-registered attributes (conceptual)
    pre_registered_attrs = {
        "custom_field_abc": DataAttribute("custom_field_abc", DataCategory.USAGE_DATA, SensitivityLevel.MEDIUM)
    }
    classifier_with_registry = DataClassifier(attribute_registry=pre_registered_attrs)
    sample_data_3 = {"custom_field_abc": "some value", "email": "another@example.com"}

    print("\n--- Classifying Sample Data 3 (with registry) ---")
    classified3 = classifier_with_registry.classify_data(sample_data_3)
    found_custom = False
    found_email_in_3 = False
    for original_key, attr in classified3:
        if attr and attr.attribute_name == "custom_field_abc":
            found_custom = True
            print(f"Key: '{original_key}' -> Attribute: {attr.attribute_name} (from registry), Category: {attr.category.value}")
            assert attr.category == DataCategory.USAGE_DATA # Check if it used the registered one
        elif attr and attr.attribute_name == "email_address":
            found_email_in_3 = True
            print(f"Key: '{original_key}' -> Attribute: {attr.attribute_name} (from rule), Category: {attr.category.value}")
    assert found_custom
    assert found_email_in_3

    print("\nAll examples executed.")
