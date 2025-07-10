# src/privacy_framework/policy_evaluator.py
"""
Evaluates if a proposed data operation is permitted based on policy and user consent.
"""

from typing import List, Optional

try:
    from .policy import PrivacyPolicy, Purpose, DataCategory, LegalBasis
    from .consent import UserConsent
    from .data_attribute import DataAttribute
except ImportError:
    # Fallback for direct execution or different project structures
    from privacy_framework.policy import PrivacyPolicy, Purpose, DataCategory, LegalBasis
    from privacy_framework.consent import UserConsent
    from privacy_framework.data_attribute import DataAttribute

class PolicyEvaluator:
    """
    Evaluates data operations against privacy policies and user consent.
    """

    def is_operation_permitted(
        self,
        policy: PrivacyPolicy,
        consent: Optional[UserConsent],
        data_attributes_involved: List[DataAttribute],
        proposed_purpose: Purpose,
        proposed_third_party: Optional[str] = None
    ) -> bool:
        """
        Checks if a proposed data operation is permitted.

        Args:
            policy (PrivacyPolicy): The relevant privacy policy.
            consent (Optional[UserConsent]): The user's consent record. Can be None.
            data_attributes_involved (List[DataAttribute]): A list of data attributes
                                                            that the operation would involve.
            proposed_purpose (Purpose): The purpose for which the data operation is intended.
            proposed_third_party (Optional[str]): The third party to whom data might be shared,
                                                  if applicable.

        Returns:
            bool: True if the operation is permitted, False otherwise.
        """

        # 1. Check Policy Allowance for the Purpose
        # The policy must explicitly list the proposed purpose.
        if proposed_purpose not in policy.purposes:
            # print(f"Denied: Purpose '{proposed_purpose.name}' not allowed by policy '{policy.policy_id}'.")
            return False

        # 2. Check Policy Allowance for Data Categories (Optional detailed check)
        # A more granular policy might specify which data categories can be used for which purposes.
        # For now, we assume if a purpose is in policy.purposes, all policy.data_categories are potentially usable for it.
        # A stricter check:
        # for da in data_attributes_involved:
        #     if da.category not in policy.data_categories:
        #         print(f"Denied: Data category '{da.category.name}' (from attribute '{da.attribute_name}') not covered by policy '{policy.policy_id}'.")
        #         return False
        # This check is implicitly covered if consent is required and consent is based on policy categories.

        # 3. Handle Consent
        # If the policy's legal basis is 'Consent', then active consent is paramount.
        if policy.legal_basis == LegalBasis.CONSENT:
            if not consent or not consent.is_active:
                # print(f"Denied: Active consent required by policy '{policy.policy_id}' but not provided or inactive.")
                return False

            # Verify consent applies to the correct policy version
            if consent.policy_id != policy.policy_id or consent.version != policy.version:
                # print(f"Denied: Consent record (ID: {consent.consent_id}) does not match policy ID/version ({policy.policy_id}/v{policy.version}).")
                return False

            # Check if all involved data attribute categories are consented to
            for da in data_attributes_involved:
                if da.category not in consent.data_categories_consented:
                    # print(f"Denied: Data category '{da.category.name}' (for attribute '{da.attribute_name}') not consented by user '{consent.user_id}'.")
                    return False

            # Check if the proposed purpose is consented to
            if proposed_purpose not in consent.purposes_consented:
                # print(f"Denied: Purpose '{proposed_purpose.name}' not consented by user '{consent.user_id}'.")
                return False

            # Check third-party sharing consent
            if proposed_third_party:
                # If third_parties_consented is empty, it might mean "no sharing with any third party".
                # If it's populated, the proposed_third_party must be in the list.
                if not consent.third_parties_consented or proposed_third_party not in consent.third_parties_consented:
                    # print(f"Denied: Sharing with third party '{proposed_third_party}' not consented by user '{consent.user_id}'.")
                    return False
            # If proposed_third_party is None, this check is skipped (operation is not for sharing).

        # 4. Handle other Legal Bases (Simplified for V1)
        # For legal bases other than consent (e.g., CONTRACT, LEGAL_OBLIGATION),
        # the operation might be permitted if it aligns with the policy's stated purpose & categories,
        # even without explicit granular consent matching every detail.
        # This logic can become very complex and domain-specific.
        # For V1 of PolicyEvaluator, if it's not LegalBasis.CONSENT, and policy allows the purpose,
        # we are more lenient, assuming the policy itself is the basis for processing.
        # A more robust implementation would check if the *specific combination* of
        # data_attributes_involved and proposed_purpose is justified by the non-consent legal basis.

        elif policy.legal_basis == LegalBasis.CONTRACT:
            # If for service delivery and part of contract, generally allowed by policy.
            if proposed_purpose != Purpose.SERVICE_DELIVERY:
                # print(f"Denied: For contractual basis, only SERVICE_DELIVERY purpose is auto-allowed by this evaluator. Proposed: {proposed_purpose.name}")
                # This is a simplification; a contract might cover other essential purposes.
                # For now, if consent is not the basis, and purpose isn't strictly SERVICE_DELIVERY for CONTRACT,
                # we'd need more sophisticated rules or fall back to requiring consent-like clarity.
                # To keep it simple: if not consent-based, and not explicitly handled, we'll be cautious.
                # For now, let's assume if it passed policy.purposes check (line 26), and it's not consent, it's okay.
                # This part needs refinement in future versions.
                pass # Covered by initial policy.purposes check

        elif policy.legal_basis == LegalBasis.LEGITIMATE_INTERESTS:
            # This requires a balancing test in GDPR, which is beyond simple rule evaluation.
            # For now, we'll treat it similarly to CONTRACT if purpose is in policy.
            # print(f"Info: Operation under 'Legitimate Interests'. Requires careful assessment beyond this basic evaluator.")
            pass

        # If all checks passed, the operation is permitted.
        # print(f"Permitted: Operation for purpose '{proposed_purpose.name}' on attributes.")
        return True


if __name__ == '__main__':
    # Example Usage
    # Setup sample Policy
    sample_policy = PrivacyPolicy(
        policy_id="sample_policy_v1",
        version=1,
        data_categories=[DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA, DataCategory.DEVICE_INFO],
        purposes=[Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS, Purpose.MARKETING],
        retention_period="1 year",
        third_parties_shared_with=["analytics.example.com", "marketing.example.com"],
        legal_basis=LegalBasis.CONSENT,
        text_summary="Sample policy for testing evaluator."
    )

    # Setup sample DataAttributes involved in an operation
    email_attribute = DataAttribute(
        attribute_name="email_address",
        category=DataCategory.PERSONAL_INFO,
        sensitivity_level=SensitivityLevel.CRITICAL,
        is_pii=True
    )
    ip_attribute = DataAttribute(
        attribute_name="ip_address",
        category=DataCategory.DEVICE_INFO,
        sensitivity_level=SensitivityLevel.MEDIUM
    )

    attributes_for_marketing_email = [email_attribute]
    attributes_for_analytics = [ip_attribute, DataAttribute("page_views", DataCategory.USAGE_DATA, SensitivityLevel.LOW)]


    # Setup Evaluator
    evaluator = PolicyEvaluator()

    print("--- Scenario 1: Consent given for Marketing Email ---")
    consent_for_marketing = UserConsent(
        consent_id="consent_mkt_001", user_id="user001", policy_id="sample_policy_v1", version=1,
        data_categories_consented=[DataCategory.PERSONAL_INFO, DataCategory.DEVICE_INFO], # Consented to PERSONAL_INFO
        purposes_consented=[Purpose.SERVICE_DELIVERY, Purpose.MARKETING], # Consented to MARKETING
        third_parties_consented=[], # No third-party sharing for this specific consent
        is_active=True
    )
    permitted = evaluator.is_operation_permitted(
        policy=sample_policy,
        consent=consent_for_marketing,
        data_attributes_involved=attributes_for_marketing_email,
        proposed_purpose=Purpose.MARKETING
    )
    print(f"Operation: Send marketing email. Permitted: {permitted} (Expected: True)")
    assert permitted

    print("\n--- Scenario 2: Consent NOT given for Analytics Purpose ---")
    # Same consent, but try to use for Analytics, which is not in consent.purposes_consented explicitly here
    # (though policy allows Analytics)
    permitted_analytics_denied_by_consent = evaluator.is_operation_permitted(
        policy=sample_policy,
        consent=consent_for_marketing, # This consent doesn't include ANALYTICS
        data_attributes_involved=attributes_for_analytics,
        proposed_purpose=Purpose.ANALYTICS
    )
    print(f"Operation: Perform analytics. Permitted: {permitted_analytics_denied_by_consent} (Expected: False because ANALYTICS not in this specific consent)")
    assert not permitted_analytics_denied_by_consent

    print("\n--- Scenario 3: Consent given for Analytics, including third-party sharing ---")
    consent_for_analytics_sharing = UserConsent(
        consent_id="consent_analytics_002", user_id="user001", policy_id="sample_policy_v1", version=1,
        data_categories_consented=[DataCategory.DEVICE_INFO, DataCategory.USAGE_DATA],
        purposes_consented=[Purpose.ANALYTICS],
        third_parties_consented=["analytics.example.com"], # Explicit consent for this third party
        is_active=True
    )
    permitted_analytics_shared = evaluator.is_operation_permitted(
        policy=sample_policy,
        consent=consent_for_analytics_sharing,
        data_attributes_involved=attributes_for_analytics,
        proposed_purpose=Purpose.ANALYTICS,
        proposed_third_party="analytics.example.com"
    )
    print(f"Operation: Share data with analytics.example.com for Analytics. Permitted: {permitted_analytics_shared} (Expected: True)")
    assert permitted_analytics_shared

    print("\n--- Scenario 4: Consent given for Analytics, but proposed third party is different ---")
    permitted_analytics_wrong_third_party = evaluator.is_operation_permitted(
        policy=sample_policy,
        consent=consent_for_analytics_sharing, # Consented to analytics.example.com
        data_attributes_involved=attributes_for_analytics,
        proposed_purpose=Purpose.ANALYTICS,
        proposed_third_party="othercorp.example.com" # Different third party
    )
    print(f"Operation: Share data with othercorp.example.com for Analytics. Permitted: {permitted_analytics_wrong_third_party} (Expected: False)")
    assert not permitted_analytics_wrong_third_party

    print("\n--- Scenario 5: No consent provided, but policy requires it ---")
    permitted_no_consent = evaluator.is_operation_permitted(
        policy=sample_policy, # LegalBasis.CONSENT
        consent=None,
        data_attributes_involved=attributes_for_marketing_email,
        proposed_purpose=Purpose.MARKETING
    )
    print(f"Operation: Send marketing email (no consent object). Permitted: {permitted_no_consent} (Expected: False)")
    assert not permitted_no_consent

    print("\n--- Scenario 6: Inactive consent ---")
    inactive_consent = UserConsent(
        consent_id="consent_inactive_003", user_id="user001", policy_id="sample_policy_v1", version=1,
        data_categories_consented=[DataCategory.PERSONAL_INFO], purposes_consented=[Purpose.MARKETING],
        is_active=False # Inactive
    )
    permitted_inactive_consent = evaluator.is_operation_permitted(
        policy=sample_policy,
        consent=inactive_consent,
        data_attributes_involved=attributes_for_marketing_email,
        proposed_purpose=Purpose.MARKETING
    )
    print(f"Operation: Send marketing email (inactive consent). Permitted: {permitted_inactive_consent} (Expected: False)")
    assert not permitted_inactive_consent

    print("\n--- Scenario 7: Policy does not allow the purpose ---")
    permitted_purpose_not_in_policy = evaluator.is_operation_permitted(
        policy=sample_policy,
        consent=consent_for_marketing, # User might consent, but policy must also allow
        data_attributes_involved=attributes_for_marketing_email,
        proposed_purpose=Purpose.RESEARCH # Assuming RESEARCH is not in sample_policy.purposes
    )
    print(f"Operation: Use for Research. Permitted: {permitted_purpose_not_in_policy} (Expected: False because RESEARCH not in policy)")
    assert not permitted_purpose_not_in_policy

    print("\n--- Scenario 8: Contractual basis for Service Delivery (no explicit consent object needed by this logic) ---")
    policy_contractual = PrivacyPolicy(
        policy_id="policy_contract_v1", version=1,
        data_categories=[DataCategory.PERSONAL_INFO], purposes=[Purpose.SERVICE_DELIVERY],
        retention_period="during contract", third_parties_shared_with=[],
        legal_basis=LegalBasis.CONTRACT, text_summary="Policy for contractual service delivery."
    )
    permitted_contractual_sd = evaluator.is_operation_permitted(
        policy=policy_contractual,
        consent=None, # No explicit consent object passed
        data_attributes_involved=[email_attribute],
        proposed_purpose=Purpose.SERVICE_DELIVERY
    )
    print(f"Operation: Service Delivery under Contract. Permitted: {permitted_contractual_sd} (Expected: True by simplified V1 logic)")
    assert permitted_contractual_sd

    print("\n--- Scenario 9: Contractual basis, but purpose is Marketing (should be denied by policy if marketing not in policy.purposes) ---")
    # Add MARKETING to policy_contractual.purposes to test evaluator's handling of non-consent basis
    policy_contractual_with_marketing = PrivacyPolicy(
        policy_id="policy_contract_v1", version=1,
        data_categories=[DataCategory.PERSONAL_INFO], purposes=[Purpose.SERVICE_DELIVERY, Purpose.MARKETING], # Marketing now in policy
        retention_period="during contract", third_parties_shared_with=[],
        legal_basis=LegalBasis.CONTRACT, text_summary="Policy for contractual service delivery + marketing."
    )
    permitted_contractual_marketing = evaluator.is_operation_permitted(
        policy=policy_contractual_with_marketing,
        consent=None,
        data_attributes_involved=[email_attribute],
        proposed_purpose=Purpose.MARKETING
    )
    # Current V1 logic: if legal_basis is not CONSENT, and purpose is in policy.purposes, it's permitted.
    # This might be too lenient for MARKETING under CONTRACT without further checks or explicit consent.
    # For now, this will pass due to simplified logic for non-consent bases.
    print(f"Operation: Marketing under Contract (policy allows Marketing). Permitted: {permitted_contractual_marketing} (Expected: True by current simplified V1 logic for non-consent basis)")
    assert permitted_contractual_marketing

    print("\n--- Scenario 10: Data category not consented ---")
    consent_missing_category = UserConsent(
        consent_id="consent_cat_004", user_id="user001", policy_id="sample_policy_v1", version=1,
        data_categories_consented=[DataCategory.DEVICE_INFO], # Only DEVICE_INFO, not PERSONAL_INFO
        purposes_consented=[Purpose.MARKETING],
        is_active=True
    )
    permitted_missing_cat = evaluator.is_operation_permitted(
        policy=sample_policy,
        consent=consent_missing_category,
        data_attributes_involved=attributes_for_marketing_email, # requires PERSONAL_INFO (email_attribute)
        proposed_purpose=Purpose.MARKETING
    )
    print(f"Operation: Send marketing email (consent misses PERSONAL_INFO). Permitted: {permitted_missing_cat} (Expected: False)")
    assert not permitted_missing_cat

    print("\nAll example PolicyEvaluator scenarios ran.")
