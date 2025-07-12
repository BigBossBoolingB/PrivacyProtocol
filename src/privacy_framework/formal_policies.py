# src/privacy_framework/formal_policies.py
"""
Defines a set of sample formal policy rules for the PolicyVerifier.
These rules are represented in a structured way that PolicyVerifier can interpret.
"""

from .policy import DataCategory, Purpose
from .data_attribute import ObfuscationMethod # For rules involving obfuscation

# Rule Format:
# Each rule is a dictionary with:
# - 'rule_id': A unique identifier for the rule.
# - 'description': A human-readable description of the rule.
# - 'conditions': A list of conditions that must ALL be met for the rule to apply to a policy or operation.
#   Each condition is a dictionary, e.g.,
#   {'field': 'purposes', 'operator': 'contains', 'value': Purpose.MARKETING}
#   {'field': 'data_categories', 'operator': 'contains_any_of', 'value': [DataCategory.HEALTH_DATA]}
# - 'assertion': What must be true if conditions are met.
#   e.g., {'field': 'data_categories_for_purpose', 'purpose': Purpose.MARKETING,
#           'operator': 'not_contains_any_of', 'value': [DataCategory.HEALTH_DATA]}
#   e.g., {'constraint': 'requires_explicit_consent_for_pii_marketing'}
#   e.g., {'obfuscation_for_purpose': Purpose.ANALYTICS, 'data_category': DataCategory.PERSONAL_INFO,
#           'must_be_one_of': [ObfuscationMethod.HASH, ObfuscationMethod.TOKENIZE]}

# This is a conceptual structure. The PolicyVerifier will need logic to parse and apply these.

FORMAL_POLICY_RULES = [
    {
        "rule_id": "FP001",
        "description": "Data Minimization for Marketing: PERSONAL_INFO for MARKETING requires explicit consent. Other uses of PERSONAL_INFO should be limited to SERVICE_DELIVERY or SECURITY unless also explicitly consented for other purposes.",
        "applies_to_policy_itself": True, # Indicates this rule is about policy structure/content
        # Conceptual check: If policy allows PERSONAL_INFO for MARKETING, it implies consent mechanisms must be robust.
        # A more direct check would be on the operation: if operation is (PERSONAL_INFO, MARKETING), then consent must be specific.
        # For this example, we'll make it a policy structure check:
        "conditions": [
            {"field": "purposes", "operator": "contains", "value": Purpose.MARKETING},
            {"field": "data_categories", "operator": "contains", "value": DataCategory.PERSONAL_INFO}
        ],
        "assertion": {
            "constraint": "policy_must_imply_consent_for_pii_marketing",
            "explanation": "Policy allows PERSONAL_INFO for MARKETING. This implies a strong consent mechanism must be in place and verified at runtime by PolicyEvaluator."
            # A true formal verifier might check if the policy text itself mentions consent for this.
        }
    },
    {
        "rule_id": "FP002",
        "description": "Retention Limit: Usage_Data for Analytics must have a retention policy not exceeding 1 year (conceptual).",
        "applies_to_policy_itself": True,
        "conditions": [
            {"field": "purposes", "operator": "contains", "value": Purpose.ANALYTICS},
            {"field": "data_categories", "operator": "contains", "value": DataCategory.USAGE_DATA}
        ],
        "assertion": {
            "field": "retention_period",
            "operator": "is_reasonable_for_analytics_usage_data", # Conceptual operator
            "value": "1 year", # Target value
            "explanation": "Policy involving USAGE_DATA for ANALYTICS should have a retention period specified, ideally <= 1 year."
        }
        # Note: 'is_reasonable_for_analytics_usage_data' is a conceptual check.
        # A real verifier would need to parse 'retention_period' string.
    },
    {
        "rule_id": "FP003",
        "description": "PII Obfuscation for Analytics: If PERSONAL_INFO is used for ANALYTICS, policy should suggest or data handling should enforce HASH or TOKENIZE if direct consent for PI for Analytics isn't primary.",
        "applies_to_policy_itself": True, # Could also be an operational rule checked by PrivacyEnforcer
        "conditions": [
            {"field": "purposes", "operator": "contains", "value": Purpose.ANALYTICS},
            {"field": "data_categories", "operator": "contains", "value": DataCategory.PERSONAL_INFO}
        ],
        "assertion": {
            "constraint": "pii_for_analytics_implies_obfuscation_or_specific_consent",
            "explanation": "Policy allows PERSONAL_INFO for ANALYTICS. System should ensure strong consent or apply obfuscation (e.g., HASH, TOKENIZE)."
            # This rule might be better enforced operationally by PrivacyEnforcer + ObfuscationEngine
            # based on actual consent. The policy verifier can check if policy *mentions* such safeguards.
        }
    },
    {
        "rule_id": "FP004",
        "description": "Third-Party Sharing of Health Data: HEALTH_DATA must never be shared with 'ThirdParty_X'.",
        "applies_to_policy_itself": True,
        "conditions": [
            {"field": "data_categories", "operator": "contains", "value": DataCategory.HEALTH_DATA}
        ],
        "assertion": {
            "field": "third_parties_shared_with",
            "operator": "not_contains",
            "value": "ThirdParty_X", # The specific disallowed third party
            "explanation": "Policy must not list 'ThirdParty_X' for sharing if HEALTH_DATA is collected."
        }
    },
    {
        "rule_id": "FP005",
        "description": "Marketing Opt-Out Principle: If MARKETING is a purpose, the overall system design (reflected by policy allowing consent) must support opt-out.",
        "applies_to_policy_itself": True,
        "conditions": [
            {"field": "purposes", "operator": "contains", "value": Purpose.MARKETING}
        ],
        "assertion": {
            "constraint": "marketing_purpose_implies_opt_out_is_possible",
            "explanation": "Policy includes MARKETING. The system must provide a way for users to opt-out (typically via consent granularity)."
        }
    }
]

if __name__ == '__main__':
    print(f"Defined {len(FORMAL_POLICY_RULES)} formal policy rules.")
    for rule in FORMAL_POLICY_RULES:
        print(f"- ID: {rule['rule_id']}, Desc: {rule['description'][:50]}...")
