import hashlib
import uuid
try:
    from .data_attribute import DataAttribute, ObfuscationMethod, DataCategory, SensitivityLevel
    from .policy import PrivacyPolicy, Purpose
    from .consent import UserConsent
    from .policy_evaluator import PolicyEvaluator # Needed for process_data_for_operation
    from .data_classifier import DataClassifier # Needed for process_data_for_operation
except ImportError: # For standalone testing
    from data_attribute import DataAttribute, ObfuscationMethod, DataCategory, SensitivityLevel
    from policy import PrivacyPolicy, Purpose
    from consent import UserConsent
    from policy_evaluator import PolicyEvaluator
    from data_classifier import DataClassifier


class ObfuscationEngine:
    def __init__(self):
        pass

    def _redact(self, value: any) -> str:
        return "[REDACTED]"

    def _hash(self, value: str) -> str:
        if not isinstance(value, str):
            value = str(value)
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def _tokenize(self, value: any) -> str:
        # Simple tokenization, could be more sophisticated (e.g., maintaining a token map)
        return f"TOKEN_{uuid.uuid4()}"

    def _encrypt(self, value: str) -> str:
        # Placeholder for actual encryption.
        # In a real system, use a proper cryptographic library (e.g., Fernet from cryptography package)
        # and manage keys securely.
        if not isinstance(value, str):
            value = str(value)
        return f"ENCRYPTED_{value[::-1]}" # Simple reversal as placeholder

    def _mask(self, value: str, visible_chars=4, from_end=True) -> str:
        if not isinstance(value, str):
            value = str(value)
        if len(value) <= visible_chars:
            return value
        if from_end:
            return "*" * (len(value) - visible_chars) + value[-visible_chars:]
        else:
            return value[:visible_chars] + "*" * (len(value) - visible_chars)

    def _aggregate(self, value: any) -> str:
        # Placeholder: In reality, this would involve combining with other data
        # and returning a summary statistic, not the value itself.
        return "[AGGREGATED_DATA_POINT]"


    def obfuscate_field(self, value: any, attribute: DataAttribute, consent_allows_raw: bool) -> any:
        """
        Obfuscates a single field based on the data attribute's preferred method,
        but only if consent does not allow raw access.

        Args:
            value: The original value of the field.
            attribute: The DataAttribute object describing the field.
            consent_allows_raw: Boolean indicating if policy/consent permits raw access.

        Returns:
            The original value if raw access is allowed, otherwise the obfuscated value.
        """
        if consent_allows_raw:
            return value

        method = attribute.obfuscation_method_preferred
        if method == ObfuscationMethod.REDACT:
            return self._redact(value)
        elif method == ObfuscationMethod.HASH:
            return self._hash(str(value)) # Ensure value is string for hashing
        elif method == ObfuscationMethod.TOKENIZE:
            return self._tokenize(value)
        elif method == ObfuscationMethod.ENCRYPT:
            return self._encrypt(str(value)) # Ensure value is string for placeholder encryption
        elif method == ObfuscationMethod.MASK:
            return self._mask(str(value))
        elif method == ObfuscationMethod.AGGREGATE:
            return self._aggregate(value)
        elif method == ObfuscationMethod.NONE: # No obfuscation preferred, but consent denied raw
             # Default to redaction if no specific method but raw is denied.
            return self._redact(value)
        else: # Should not happen if ObfuscationMethod enum is used correctly
            return value # Fallback to original if unknown method (or raise error)

    def process_data_for_operation(self,
                                   raw_data: dict,
                                   policy: PrivacyPolicy,
                                   consent: UserConsent | None,
                                   proposed_purpose: Purpose,
                                   data_classifier: DataClassifier, # Pass classifier instance
                                   policy_evaluator: PolicyEvaluator, # Pass evaluator instance
                                   proposed_third_party: str | None = None
                                   ) -> dict:
        """
        Processes a dictionary of raw data, applying obfuscation based on policy,
        user consent, and the proposed operation.

        Args:
            raw_data: The input dictionary of data.
            policy: The governing PrivacyPolicy.
            consent: The active UserConsent, or None.
            proposed_purpose: The Purpose of the data operation.
            data_classifier: An instance of DataClassifier.
            policy_evaluator: An instance of PolicyEvaluator.
            proposed_third_party: Optional third party involved.

        Returns:
            A new dictionary with fields processed (either raw or obfuscated).
        """
        if not isinstance(raw_data, dict):
            raise ValueError("raw_data must be a dictionary.")

        classified_fields = data_classifier.classify_data(raw_data)
        processed_data = {}

        for original_key, attribute in classified_fields:
            original_value = raw_data[original_key]
            if attribute is None: # Should not happen with current classifier's fallback
                processed_data[original_key] = original_value # Keep as is if unclassifiable
                continue

            # Check if raw access to this specific attribute is permitted for the operation
            # is_operation_permitted expects a list of data_attributes
            is_raw_permitted = policy_evaluator.is_operation_permitted(
                policy=policy,
                consent=consent,
                data_attributes=[attribute], # Evaluate permission for this single attribute
                proposed_purpose=proposed_purpose,
                proposed_third_party=proposed_third_party
            )

            processed_value = self.obfuscate_field(original_value, attribute, is_raw_permitted)
            processed_data[original_key] = processed_value

        return processed_data


if __name__ == '__main__':
    engine = ObfuscationEngine()
    classifier = DataClassifier() # Using default classifier
    evaluator = PolicyEvaluator()

    # --- Test individual obfuscation methods ---
    print("--- Individual Obfuscation Method Tests ---")
    print(f"Redact 'secret': {engine._redact('secret')}")
    print(f"Hash 'secret123': {engine._hash('secret123')}")
    print(f"Tokenize 'user@example.com': {engine._tokenize('user@example.com')}")
    print(f"Encrypt 'password': {engine._encrypt('password')}") # Placeholder
    print(f"Mask '1234567890': {engine._mask('1234567890')}")
    print(f"Mask 'short': {engine._mask('short')}")
    print(f"Aggregate 100: {engine._aggregate(100)}")

    # --- Test obfuscate_field ---
    print("\n--- obfuscate_field Tests ---")
    email_attr = DataAttribute("email", DataCategory.PERSONAL_INFO, SensitivityLevel.MEDIUM, obfuscation_method_preferred=ObfuscationMethod.HASH)
    api_key_attr = DataAttribute("api_key", DataCategory.TECHNICAL_INFO, SensitivityLevel.CRITICAL, obfuscation_method_preferred=ObfuscationMethod.REDACT)
    pref_attr = DataAttribute("preference", DataCategory.USAGE_DATA, SensitivityLevel.LOW, obfuscation_method_preferred=ObfuscationMethod.NONE)

    # Scenario 1: Consent allows raw
    print(f"Email ('user@example.com'), raw allowed: {engine.obfuscate_field('user@example.com', email_attr, True)}")
    # Scenario 2: Consent denies raw, HASH preferred
    print(f"Email ('user@example.com'), raw denied (HASH): {engine.obfuscate_field('user@example.com', email_attr, False)}")
    # Scenario 3: Consent denies raw, REDACT preferred
    print(f"API Key ('verysecretkey'), raw denied (REDACT): {engine.obfuscate_field('verysecretkey', api_key_attr, False)}")
    # Scenario 4: Consent denies raw, NONE preferred (should default to REDACT)
    print(f"Preference ('darkmode'), raw denied (NONE): {engine.obfuscate_field('darkmode', pref_attr, False)}")


    # --- Test process_data_for_operation ---
    print("\n--- process_data_for_operation Tests ---")
    sample_policy = PrivacyPolicy(
        policy_id="obfuscation_test_policy",
        data_categories=[DataCategory.PERSONAL_INFO, DataCategory.TECHNICAL_INFO, DataCategory.USAGE_DATA],
        purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS]
    )
    sample_user_data = {
        "email": "test@example.com",
        "ip_address": "192.168.1.100",
        "page_views": 50,
        "user_notes": "This is a sensitive note." # Will be classified as OTHER, LOW
    }

    # User consent: Allows PERSONAL_INFO for SERVICE_DELIVERY, but not TECHNICAL_INFO for SERVICE_DELIVERY
    # Allows USAGE_DATA for ANALYTICS
    sample_consent_scenario1 = UserConsent(
        user_id="user_obf_test", policy_id=sample_policy.policy_id,
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS]
        # No explicit consent for TECHNICAL_INFO for SERVICE_DELIVERY
    )
    # Make email attribute prefer HASH, ip_address prefer REDACT, page_views NONE for this test setup
    # This would typically come from a richer DataClassifier or attribute registry
    classifier.attribute_registry["email_address"] = DataAttribute(attribute_name="email_address", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM, obfuscation_method_preferred=ObfuscationMethod.HASH)
    classifier.attribute_registry["ip_address"] = DataAttribute(attribute_name="ip_address", category=DataCategory.TECHNICAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM, obfuscation_method_preferred=ObfuscationMethod.REDACT)
    classifier.attribute_registry["user_interaction"] = DataAttribute(attribute_name="user_interaction", category=DataCategory.USAGE_DATA, sensitivity_level=SensitivityLevel.LOW, obfuscation_method_preferred=ObfuscationMethod.NONE) # for page_views
    classifier.attribute_registry["user_notes"] = DataAttribute(attribute_name="user_notes", category=DataCategory.OTHER, sensitivity_level=SensitivityLevel.LOW, obfuscation_method_preferred=ObfuscationMethod.REDACT)


    print(f"\nInput data: {sample_user_data}")
    # Scenario A: Process for SERVICE_DELIVERY
    processed_A = engine.process_data_for_operation(
        raw_data=sample_user_data,
        policy=sample_policy,
        consent=sample_consent_scenario1,
        proposed_purpose=Purpose.SERVICE_DELIVERY,
        data_classifier=classifier,
        policy_evaluator=evaluator
    )
    print(f"Processed for SERVICE_DELIVERY: {processed_A}")
    # Expected: email raw (consented for SERVICE_DELIVERY), ip_address REDACTED (TECHNICAL_INFO not consented for SERVICE_DELIVERY)
    # page_views REDACTED (USAGE_DATA not consented for SERVICE_DELIVERY), user_notes raw (OTHER, LOW, assumed permitted if not specified in consent for service delivery)
    # Let's refine consent for clarity:
    sample_consent_scenario1.data_categories_consented = [DataCategory.PERSONAL_INFO] # Only personal info for service delivery
    sample_consent_scenario1.purposes_consented = [Purpose.SERVICE_DELIVERY]

    processed_A_refined = engine.process_data_for_operation(
        raw_data=sample_user_data, policy=sample_policy, consent=sample_consent_scenario1,
        proposed_purpose=Purpose.SERVICE_DELIVERY, data_classifier=classifier, policy_evaluator=evaluator
    )
    print(f"Processed (refined consent) for SERVICE_DELIVERY: {processed_A_refined}")
    assert processed_A_refined["email"] == "test@example.com"
    assert processed_A_refined["ip_address"] == "[REDACTED]" # Not consented for SERVICE_DELIVERY
    assert processed_A_refined["page_views"] == "[REDACTED]" # Not consented for SERVICE_DELIVERY
    assert processed_A_refined["user_notes"] == "[REDACTED]" # OTHER, LOW, but consent for SERVICE_DELIVERY is only for PERSONAL_INFO

    # Scenario B: Process for ANALYTICS (consent: USAGE_DATA for ANALYTICS)
    sample_consent_scenario2 = UserConsent(
        user_id="user_obf_test", policy_id=sample_policy.policy_id,
        data_categories_consented=[DataCategory.USAGE_DATA],
        purposes_consented=[Purpose.ANALYTICS]
    )
    processed_B = engine.process_data_for_operation(
        raw_data=sample_user_data,
        policy=sample_policy,
        consent=sample_consent_scenario2,
        proposed_purpose=Purpose.ANALYTICS,
        data_classifier=classifier,
        policy_evaluator=evaluator
    )
    print(f"Processed for ANALYTICS: {processed_B}")
    # Expected: email HASHED (not consented for ANALYTICS), ip_address REDACTED (not consented for ANALYTICS)
    # page_views RAW (consented for ANALYTICS), user_notes REDACTED (not consented for ANALYTICS)
    assert processed_B["email"].startswith("TOKEN_") or len(processed_B["email"]) == 64 # Hashed by rule in classifier
    assert processed_B["ip_address"] == "[REDACTED]"
    assert processed_B["page_views"] == 50
    assert processed_B["user_notes"] == "[REDACTED]"

    print("\nAll examples executed.")
