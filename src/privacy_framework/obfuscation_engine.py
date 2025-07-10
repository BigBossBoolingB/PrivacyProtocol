# src/privacy_framework/obfuscation_engine.py
"""
Applies obfuscation techniques to data based on classification, policy, and consent.
"""
import hashlib
from typing import List, Dict, Any, Optional

try:
    from .data_attribute import DataAttribute, ObfuscationMethod, DataCategory
    from .policy import PrivacyPolicy, Purpose
    from .consent import UserConsent
    from .policy_evaluator import PolicyEvaluator # Assuming PolicyEvaluator is in the same directory level
except ImportError:
    # Fallback for direct execution or different project structures
    from privacy_framework.data_attribute import DataAttribute, ObfuscationMethod, DataCategory
    from privacy_framework.policy import PrivacyPolicy, Purpose
    from privacy_framework.consent import UserConsent
    from privacy_framework.policy_evaluator import PolicyEvaluator


class ObfuscationEngine:
    """
    Applies various obfuscation techniques to data based on DataAttribute's
    preferred method and policy/consent evaluation.
    """

    def obfuscate_field(self, value: Any, method: ObfuscationMethod) -> Any:
        """
        Applies a specific obfuscation method to a single value.
        """
        if method == ObfuscationMethod.NONE:
            return value
        if method == ObfuscationMethod.REDACT:
            return "[REDACTED]"
        if method == ObfuscationMethod.HASH:
            if value is None: return None # Avoid hashing None
            return hashlib.sha256(str(value).encode()).hexdigest()
        if method == ObfuscationMethod.TOKENIZE:
            if value is None: return None
            # Simple tokenization using part of a hash
            return f"TOKEN_{hashlib.md5(str(value).encode()).hexdigest()[:12]}"
        if method == ObfuscationMethod.ENCRYPT:
            # Placeholder: Real encryption would involve keys and a crypto library
            return f"[ENCRYPTED({value})_PLACEHOLDER]"
        if method == ObfuscationMethod.MASK:
            s_value = str(value)
            if "@" in s_value: # Basic email masking
                parts = s_value.split('@')
                if len(parts) == 2 and parts[0] and parts[1]: # Check if it's a plausible email structure
                    return parts[0][0] + "****" + "@" + parts[1]
                else: # Not a typical email format or too short to mask meaningfully
                    return s_value[:1] + "****" if s_value else "****"
            elif len(s_value) > 4: # Generic masking for longer strings (e.g., phone numbers, IDs)
                return s_value[:2] + "****" + s_value[-2:]
            elif len(s_value) > 0: # Short strings
                 return s_value[0] + "****"
            else:
                return "****" # Empty string
        if method == ObfuscationMethod.AGGREGATE:
            # Placeholder: Real aggregation depends on context and other data.
            # This indicates the data point should be part of an aggregate, not shown individually.
            return "[VALUE_FOR_AGGREGATION_ONLY]"

        return value # Default to returning original if method unknown (should not happen with Enum)

    def process_data_attributes(
        self,
        raw_data: Dict[str, Any],
        classified_attributes: List[DataAttribute],
        policy: PrivacyPolicy,
        consent: Optional[UserConsent],
        proposed_purpose: Purpose,
        policy_evaluator: PolicyEvaluator,
        proposed_third_party: Optional[str] = None,
        default_obfuscation_if_denied: ObfuscationMethod = ObfuscationMethod.REDACT
    ) -> Dict[str, Any]:
        """
        Processes a dictionary of raw data, applying obfuscation based on policy evaluation
        for each attribute.

        Args:
            raw_data (Dict[str, Any]): The raw data dictionary (flat for this version).
            classified_attributes (List[DataAttribute]): A list of DataAttribute objects corresponding
                                                         to the keys in raw_data.
            policy (PrivacyPolicy): The governing privacy policy.
            consent (Optional[UserConsent]): The user's consent.
            proposed_purpose (Purpose): The purpose of the data operation.
            policy_evaluator (PolicyEvaluator): The evaluator instance.
            proposed_third_party (Optional[str]): The third party, if any.
            default_obfuscation_if_denied (ObfuscationMethod): Method to apply if an operation on
                                                              an attribute is denied and its preferred
                                                              method is NONE.
        Returns:
            Dict[str, Any]: A new dictionary with data fields processed (obfuscated or original).
        """
        processed_data = {}

        # Create a map of attribute_name to DataAttribute for easy lookup
        attribute_map: Dict[str, DataAttribute] = {attr.attribute_name: attr for attr in classified_attributes}

        for key, original_value in raw_data.items():
            attribute = attribute_map.get(key)

            if not attribute:
                # Data field not classified, handle as per a default policy (e.g., redact or raise error)
                # print(f"Warning: Data field '{key}' not found in classified attributes. Applying default redaction.")
                processed_data[key] = self.obfuscate_field(original_value, default_obfuscation_if_denied)
                continue

            # Evaluate permission for this specific attribute and its value in the context of the operation
            is_permitted = policy_evaluator.is_operation_permitted(
                policy=policy,
                consent=consent,
                data_attributes_involved=[attribute], # Evaluate for this single attribute
                proposed_purpose=proposed_purpose,
                proposed_third_party=proposed_third_party
            )

            if is_permitted:
                processed_data[key] = original_value
            else:
                # Operation not permitted for the raw data. Apply obfuscation.
                # Use the attribute's preferred method, or a stricter default if preferred is NONE.
                obfuscation_method_to_apply = attribute.obfuscation_method_preferred
                if obfuscation_method_to_apply == ObfuscationMethod.NONE:
                    obfuscation_method_to_apply = default_obfuscation_if_denied

                processed_data[key] = self.obfuscate_field(original_value, obfuscation_method_to_apply)
                # print(f"Info: Field '{key}' for purpose '{proposed_purpose.name}' was denied. Applied obfuscation: {obfuscation_method_to_apply.name}")

        return processed_data


if __name__ == '__main__':
    engine = ObfuscationEngine()
    evaluator = PolicyEvaluator() # Needed for process_data_attributes example

    print("--- Testing obfuscate_field ---")
    print(f"REDACT 'secret data': {engine.obfuscate_field('secret data', ObfuscationMethod.REDACT)}")
    print(f"HASH 'secret data': {engine.obfuscate_field('secret data', ObfuscationMethod.HASH)}")
    print(f"TOKENIZE 'secret data': {engine.obfuscate_field('secret data', ObfuscationMethod.TOKENIZE)}")
    print(f"ENCRYPT 'secret data': {engine.obfuscate_field('secret data', ObfuscationMethod.ENCRYPT)}")
    print(f"MASK 'user@example.com': {engine.obfuscate_field('user@example.com', ObfuscationMethod.MASK)}")
    print(f"MASK '1234567890': {engine.obfuscate_field('1234567890', ObfuscationMethod.MASK)}")
    print(f"MASK 'abc': {engine.obfuscate_field('abc', ObfuscationMethod.MASK)}")
    print(f"AGGREGATE '123': {engine.obfuscate_field(123, ObfuscationMethod.AGGREGATE)}")
    print(f"NONE 'secret data': {engine.obfuscate_field('secret data', ObfuscationMethod.NONE)}")

    # Example for process_data_attributes
    print("\n--- Testing process_data_attributes ---")
    # Sample policy (strict, requires consent for everything)
    test_policy = PrivacyPolicy(
        policy_id="test_obf_policy", version=1,
        data_categories=[DataCategory.PERSONAL_INFO, DataCategory.DEVICE_INFO],
        purposes=[Purpose.MARKETING, Purpose.ANALYTICS],
        legal_basis=LegalBasis.CONSENT, text_summary="Test policy for obfuscation",
        third_parties_shared_with=["ads.partner.com"]
    )
    # Sample consent (allows PI for marketing, but not device_info for marketing)
    test_consent = UserConsent(
        consent_id="c_obf_001", user_id="user_obf", policy_id="test_obf_policy", version=1,
        data_categories_consented=[DataCategory.PERSONAL_INFO], # Only PI
        purposes_consented=[Purpose.MARKETING], # Only Marketing
        third_parties_consented=[], # No third party sharing
        is_active=True
    )
    # Sample raw data and its classification
    raw_user_data = {
        "email": "test@example.com", # PI
        "device_id": "xyz123abc",    # Device Info
        "last_seen": "2024-01-01"    # Other
    }
    classified_attrs = [
        DataAttribute("email", DataCategory.PERSONAL_INFO, SensitivityLevel.CRITICAL, True, ObfuscationMethod.HASH),
        DataAttribute("device_id", DataCategory.DEVICE_INFO, SensitivityLevel.MEDIUM, False, ObfuscationMethod.REDACT),
        DataAttribute("last_seen", DataCategory.OTHER, SensitivityLevel.LOW, False, ObfuscationMethod.NONE)
    ]

    print(f"\nOriginal Data: {raw_user_data}")
    print(f"Policy: Marketing requires consent for PERSONAL_INFO and DEVICE_INFO.")
    print(f"Consent: Allows PERSONAL_INFO for MARKETING. Denies DEVICE_INFO for MARKETING.")

    # Scenario 1: Marketing purpose
    print("\nScenario: Processing for MARKETING purpose")
    processed_for_marketing = engine.process_data_attributes(
        raw_data=raw_user_data,
        classified_attributes=classified_attrs,
        policy=test_policy,
        consent=test_consent,
        proposed_purpose=Purpose.MARKETING,
        policy_evaluator=evaluator
    )
    print(f"Processed for Marketing: {processed_for_marketing}")
    # Expected: email (PI) is allowed by consent for Marketing, so original.
    # device_id (Device Info) is NOT allowed by consent for Marketing (category not consented), so REDACT (its preferred method).
    # last_seen (Other) is not in policy's data_categories, so PolicyEvaluator might deny.
    # If PolicyEvaluator denies based on policy.data_categories, then last_seen will be REDACTED (default_obfuscation_if_denied).
    # Let's assume PolicyEvaluator's is_operation_permitted([attribute]) focuses on consent if basis is CONSENT.
    # PolicyEvaluator checks if attribute.category is in consent.data_categories_consented.
    # For "last_seen", its category OTHER is not in test_consent.data_categories_consented. So it will be obfuscated.
    # Its preferred method is NONE, so it will use default_obfuscation_if_denied (REDACT).

    # Expected:
    # email: 'test@example.com' (permitted)
    # device_id: '[REDACTED]' (denied by consent for this purpose, preferred method is REDACT)
    # last_seen: '[REDACTED]' (denied by consent as OTHER not in consented categories, preferred NONE -> default REDACT)

    assert processed_for_marketing['email'] == "test@example.com"
    assert processed_for_marketing['device_id'] == "[REDACTED]" # Based on DataAttribute's preferred method
    assert processed_for_marketing['last_seen'] == "[REDACTED]" # Preferred is NONE, so default_obfuscation_if_denied applies


    # Scenario 2: Analytics purpose (not consented by user at all)
    print("\nScenario: Processing for ANALYTICS purpose (user has not consented to this purpose)")
    processed_for_analytics = engine.process_data_attributes(
        raw_data=raw_user_data,
        classified_attributes=classified_attrs,
        policy=test_policy, # Policy allows ANALYTICS
        consent=test_consent, # Consent does NOT allow ANALYTICS
        proposed_purpose=Purpose.ANALYTICS,
        policy_evaluator=evaluator
    )
    print(f"Processed for Analytics: {processed_for_analytics}")
    # Expected: All fields should be obfuscated as the purpose ANALYTICS is not consented.
    # email: HASHED (its preferred method)
    # device_id: REDACTED (its preferred method)
    # last_seen: REDACTED (preferred NONE -> default REDACT)
    assert processed_for_analytics['email'] == hashlib.sha256(str(raw_user_data['email']).encode()).hexdigest()
    assert processed_for_analytics['device_id'] == "[REDACTED]"
    assert processed_for_analytics['last_seen'] == "[REDACTED]"

    print("\nObfuscation Engine Demo Complete.")
