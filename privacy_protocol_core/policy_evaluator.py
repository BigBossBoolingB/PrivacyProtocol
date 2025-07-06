try:
    from .policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis
    from .consent import UserConsent
    from .data_attribute import DataAttribute
except ImportError: # For standalone testing
    from policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis
    from consent import UserConsent
    from data_attribute import DataAttribute

class PolicyEvaluator:
    def __init__(self):
        """
        Initializes the PolicyEvaluator.
        This evaluator checks if a proposed data operation is permitted based on
        a given privacy policy and user consent.
        """
        pass

    def is_operation_permitted(self, policy: PrivacyPolicy,
                               consent: UserConsent | None,
                               data_attributes: list[DataAttribute],
                               proposed_purpose: Purpose,
                               proposed_third_party: str | None = None) -> bool:
        """
        Evaluates if a proposed data operation is permitted.

        Args:
            policy: The PrivacyPolicy object governing the data.
            consent: The UserConsent object (if any) from the user. Can be None.
            data_attributes: A list of DataAttribute objects involved in the operation.
            proposed_purpose: The Purpose enum value for which data is being used.
            proposed_third_party: Optional name of the third party if data is shared.

        Returns:
            True if the operation is permitted, False otherwise.
        """

        if not isinstance(policy, PrivacyPolicy):
            # print("Debug: Invalid policy object.")
            return False
        if consent is not None and not isinstance(consent, UserConsent):
            # print("Debug: Invalid consent object (if provided).")
            return False
        if not isinstance(data_attributes, list) or not all(isinstance(da, DataAttribute) for da in data_attributes):
            # print("Debug: data_attributes must be a list of DataAttribute objects.")
            return False
        if not isinstance(proposed_purpose, Purpose):
            # print("Debug: proposed_purpose must be a Purpose enum.")
            return False

        # 1. Policy Checks: Does the policy generally allow this?
        # 1a. Does the policy list this purpose?
        if proposed_purpose not in policy.purposes:
            # print(f"Debug: Proposed purpose '{proposed_purpose.value}' not in policy purposes: {[p.value for p in policy.purposes]}.")
            return False

        # 1b. Do all data attribute categories exist in the policy's declared data categories?
        #     (This is a simplified check. A more advanced policy might link specific categories to specific purposes.)
        policy_data_categories_values = {dc.value for dc in policy.data_categories}
        for attr in data_attributes:
            if attr.category and attr.category.value not in policy_data_categories_values:
                # print(f"Debug: Attribute category '{attr.category.value}' (from attribute '{attr.attribute_name}') not declared in policy data categories.")
                return False

        # 2. Consent Checks: If consent is the basis (or one of them), is it granted?
        #    For now, we assume consent is primary if provided.
        #    A more advanced evaluator would check policy.legal_basis and act accordingly.
        #    E.g., if LegalBasis.CONTRACT is present for a purpose, consent might not be needed for THAT purpose.

        # If no consent object is provided, but the policy might rely on other legal bases,
        # this check would need to be more sophisticated. For now, if consent is None,
        # and we are strictly checking consent, then it's a denial unless the policy explicitly
        # states another basis for THIS specific purpose and data. This part is simplified.

        # For this implementation, if consent is required (e.g. policy lists CONSENT as a legal basis,
        # or it's the default check path), then a missing or inactive consent means denial.
        # We will assume for now that if a consent object is passed, it's the one to check.
        # If consent is None, we'll deny, simplifying the legal basis check for this iteration.

        if not consent or not consent.is_active:
            # print("Debug: Consent is missing or inactive.")
            # Future: Check if policy allows this operation under another legal basis
            # for this specific purpose and data categories if consent is not the only basis.
            # For example, if policy.legal_basis for this purpose is 'Legal_Obligation'.
            # This is simplified: if consent object is not active, deny.
            return False

        # 2a. Are all data categories of the attributes consented to?
        consented_data_categories_values = {dc.value for dc in consent.data_categories_consented}
        for attr in data_attributes:
            if attr.category and attr.category.value not in consented_data_categories_values:
                # print(f"Debug: Data category '{attr.category.value}' (from attribute '{attr.attribute_name}') not in consented categories.")
                return False

        # 2b. Is the proposed purpose consented to?
        if proposed_purpose not in consent.purposes_consented:
            # print(f"Debug: Proposed purpose '{proposed_purpose.value}' not in consented purposes.")
            return False

        # 2c. If sharing with a third party, is that third party consented to for this purpose?
        #     This is a simplification. Real consent might be more granular, e.g., consent to share
        #     [categoryX] with [ThirdPartyY] for [PurposeZ].
        #     Current UserConsent has a flat list of third_parties_consented.
        if proposed_third_party:
            # This implies that if any third_party is involved, it must be in the flat list.
            # A more advanced model might have specific consent per purpose per third party.
            if proposed_third_party not in consent.third_parties_consented:
                # print(f"Debug: Proposed third party '{proposed_third_party}' not in consented third parties.")
                # Allow a wildcard "*" in consented_third_parties to mean consent to share with any third party for consented purposes/categories.
                if "*" not in consent.third_parties_consented:
                    return False

        # All checks passed
        return True


if __name__ == '__main__':
    # --- Setup Example Data ---
    # Policy
    policy1 = PrivacyPolicy(
        policy_id="policy_eval_test1",
        version="1.0",
        data_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.TECHNICAL_INFO],
        purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS, Purpose.MARKETING, Purpose.SECURITY],
        legal_basis=[LegalBasis.CONSENT, LegalBasis.CONTRACT],
        third_parties_shared_with=["AnalyticsCorp", "MarketingPartner"] # Parties the policy *might* share with
    )

    # Data Attributes
    email_attr = DataAttribute(attribute_name="email", category=DataCategory.PERSONAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM)
    ip_attr = DataAttribute(attribute_name="ip_address", category=DataCategory.TECHNICAL_INFO, sensitivity_level=SensitivityLevel.MEDIUM)
    click_attr = DataAttribute(attribute_name="click_event", category=DataCategory.USAGE_DATA, sensitivity_level=SensitivityLevel.LOW)
    photo_attr = DataAttribute(attribute_name="profile_photo", category=DataCategory.BIOMETRIC_DATA, sensitivity_level=SensitivityLevel.HIGH) # Not in policy1's categories

    # User Consents
    consent_full_user1 = UserConsent(
        user_id="user1", policy_id=policy1.policy_id, policy_version="1.0",
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.TECHNICAL_INFO],
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS, Purpose.MARKETING],
        third_parties_consented=["AnalyticsCorp", "MarketingPartner", "CustomerSupportTool"] # User consents to these
    )

    consent_limited_user2 = UserConsent(
        user_id="user2", policy_id=policy1.policy_id, policy_version="1.0",
        data_categories_consented=[DataCategory.PERSONAL_INFO],
        purposes_consented=[Purpose.SERVICE_DELIVERY],
        third_parties_consented=[] # Consents to no third party sharing explicitly
    )

    consent_marketing_only_user3 = UserConsent(
        user_id="user3", policy_id=policy1.policy_id, policy_version="1.0",
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
        purposes_consented=[Purpose.MARKETING],
        third_parties_consented=["MarketingPartner"]
    )

    consent_wildcard_third_party_user4 = UserConsent(
        user_id="user4", policy_id=policy1.policy_id, policy_version="1.0",
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA],
        purposes_consented=[Purpose.ANALYTICS],
        third_parties_consented=["*"] # Consent to share with ANY third party for analytics
    )

    evaluator = PolicyEvaluator()

    # --- Test Cases ---
    print("--- PolicyEvaluator Tests ---")

    # Test 1: Fully permitted operation
    op1_attrs = [email_attr, click_attr]
    op1_purpose = Purpose.ANALYTICS
    op1_tp = "AnalyticsCorp"
    permitted1 = evaluator.is_operation_permitted(policy1, consent_full_user1, op1_attrs, op1_purpose, op1_tp)
    print(f"Test 1 (User1, Analytics with AnalyticsCorp): Permitted = {permitted1}")
    assert permitted1 == True

    # Test 2: Denied - Purpose not consented by user2
    op2_attrs = [email_attr]
    op2_purpose = Purpose.MARKETING # User2 only consented to SERVICE_DELIVERY
    permitted2 = evaluator.is_operation_permitted(policy1, consent_limited_user2, op2_attrs, op2_purpose)
    print(f"Test 2 (User2, Marketing for email): Permitted = {permitted2}")
    assert permitted2 == False

    # Test 3: Denied - Data category (BIOMETRIC_DATA) not in policy
    op3_attrs = [photo_attr] # photo_attr is BIOMETRIC_DATA
    op3_purpose = Purpose.SERVICE_DELIVERY
    permitted3 = evaluator.is_operation_permitted(policy1, consent_full_user1, op3_attrs, op3_purpose)
    print(f"Test 3 (User1, Service Delivery for photo): Permitted = {permitted3}")
    assert permitted3 == False

    # Test 4: Denied - Data category (TECHNICAL_INFO for ip_attr) not consented by user2
    op4_attrs = [ip_attr] # User2 only consented to PERSONAL_INFO
    op4_purpose = Purpose.SERVICE_DELIVERY
    permitted4 = evaluator.is_operation_permitted(policy1, consent_limited_user2, op4_attrs, op4_purpose)
    print(f"Test 4 (User2, Service Delivery for IP): Permitted = {permitted4}")
    assert permitted4 == False

    # Test 5: Denied - Third party not consented by user2
    op5_attrs = [email_attr]
    op5_purpose = Purpose.SERVICE_DELIVERY # This purpose is consented by user2 for email
    op5_tp = "AnalyticsCorp" # User2 consented to no third parties
    permitted5 = evaluator.is_operation_permitted(policy1, consent_limited_user2, op5_attrs, op5_purpose, op5_tp)
    print(f"Test 5 (User2, Service Delivery for email, share with AnalyticsCorp): Permitted = {permitted5}")
    assert permitted5 == False

    # Test 6: Permitted - No third party proposed, user2 consented to service delivery for personal info
    op6_attrs = [email_attr]
    op6_purpose = Purpose.SERVICE_DELIVERY
    permitted6 = evaluator.is_operation_permitted(policy1, consent_limited_user2, op6_attrs, op6_purpose, None)
    print(f"Test 6 (User2, Service Delivery for email, no third party): Permitted = {permitted6}")
    assert permitted6 == True

    # Test 7: Denied - Purpose (SECURITY) not consented by user1 (consent_full_user1)
    op7_attrs = [ip_attr]
    op7_purpose = Purpose.SECURITY # Policy allows it, but user1's consent_full_user1 doesn't list it
    permitted7 = evaluator.is_operation_permitted(policy1, consent_full_user1, op7_attrs, op7_purpose)
    print(f"Test 7 (User1, Security for IP): Permitted = {permitted7}")
    assert permitted7 == False

    # Test 8: Denied - Consent is None
    op8_attrs = [email_attr]
    op8_purpose = Purpose.SERVICE_DELIVERY
    permitted8 = evaluator.is_operation_permitted(policy1, None, op8_attrs, op8_purpose)
    print(f"Test 8 (No consent, Service Delivery for email): Permitted = {permitted8}")
    assert permitted8 == False

    # Test 9: Denied - Consent is inactive
    consent_inactive_user1 = UserConsent(
        user_id="user1", policy_id=policy1.policy_id, policy_version="1.0",
        data_categories_consented=[DataCategory.PERSONAL_INFO], purposes_consented=[Purpose.SERVICE_DELIVERY],
        is_active=False
    )
    op9_attrs = [email_attr]
    op9_purpose = Purpose.SERVICE_DELIVERY
    permitted9 = evaluator.is_operation_permitted(policy1, consent_inactive_user1, op9_attrs, op9_purpose)
    print(f"Test 9 (Inactive consent, Service Delivery for email): Permitted = {permitted9}")
    assert permitted9 == False

    # Test 10: Denied - Purpose (RESEARCH_DEVELOPMENT) not in policy at all
    op10_attrs = [click_attr]
    op10_purpose = Purpose.RESEARCH_DEVELOPMENT # Not in policy1.purposes
    permitted10 = evaluator.is_operation_permitted(policy1, consent_full_user1, op10_attrs, op10_purpose)
    print(f"Test 10 (User1, Research & Dev for click): Permitted = {permitted10}")
    assert permitted10 == False

    # Test 11: Permitted - Wildcard third party consent
    op11_attrs = [email_attr, click_attr]
    op11_purpose = Purpose.ANALYTICS
    op11_tp = "SomeNewAnalyticsCorp" # Not explicitly listed, but user4 has wildcard
    permitted11 = evaluator.is_operation_permitted(policy1, consent_wildcard_third_party_user4, op11_attrs, op11_purpose, op11_tp)
    print(f"Test 11 (User4, Analytics with new TP, wildcard consent): Permitted = {permitted11}")
    assert permitted11 == True

    # Test 12: Denied - Wildcard third party consent but purpose not consented
    op12_attrs = [email_attr]
    op12_purpose = Purpose.MARKETING # User4 only consented to Analytics
    op12_tp = "SomeMarketingPartner"
    permitted12 = evaluator.is_operation_permitted(policy1, consent_wildcard_third_party_user4, op12_attrs, op12_purpose, op12_tp)
    print(f"Test 12 (User4, Marketing with new TP, wildcard consent but wrong purpose): Permitted = {permitted12}")
    assert permitted12 == False

    print("\nAll PolicyEvaluator examples executed.")
