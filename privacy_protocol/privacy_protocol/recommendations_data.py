# Data store for actionable recommendations

# Recommendation IDs (can be used for more structured referencing if needed later)
REC_ID_OPT_OUT_DATA_SELLING = 'OPT_OUT_DATA_SELLING'
REC_ID_LIMIT_AD_TRACKING_GENERAL = 'LIMIT_AD_TRACKING_GENERAL'
REC_ID_REQUEST_DATA_DELETION_INFO = 'REQUEST_DATA_DELETION_INFO'
REC_ID_REVIEW_THIRD_PARTY_POLICIES = 'REVIEW_THIRD_PARTY_POLICIES'
REC_ID_MONITOR_POLICY_CHANGES = 'MONITOR_POLICY_CHANGES'
REC_ID_CHILDRENS_PRIVACY_CAUTION = 'CHILDRENS_PRIVACY_CAUTION'
REC_ID_REVIEW_SECURITY_PRACTICES = 'REVIEW_SECURITY_PRACTICES'
REC_ID_UNDERSTAND_DATA_RETENTION = 'UNDERSTAND_DATA_RETENTION'
REC_ID_MANAGE_COOKIES = 'MANAGE_COOKIES'

RECOMMENDATIONS_DATA = [
    {
        'id': REC_ID_OPT_OUT_DATA_SELLING,
        'title': "Consider Opting Out of Data Selling",
        'text': "This policy mentions practices that might be considered data selling. Look for a 'Do Not Sell My Personal Information' link or section in their privacy settings or website footer to opt out. You may also need to contact them directly.",
        'triggers': [
            {'ai_category': 'Data Selling', 'min_concern': ['High', 'Medium']},
            # Future: {'keyword_category': 'Specific Data Selling Keyword', 'min_concern': ['High', 'Medium']}
        ]
    },
    {
        'id': REC_ID_LIMIT_AD_TRACKING_GENERAL,
        'title': "Limit Ad Tracking",
        'text': "The policy mentions tracking, potentially for advertising. You can often limit ad tracking via your device settings (e.g., iOS: Privacy > Tracking; Android: Settings > Google > Ads) or by using browser extensions that block trackers.",
        'triggers': [
            {'ai_category': 'Cookies and Tracking Technologies', 'min_concern': ['High', 'Medium']},
            # Consider if 'Data Sharing' for ads should also trigger this, if distinguishable
        ]
    },
    {
        'id': REC_ID_REQUEST_DATA_DELETION_INFO,
        'title': "Understand Data Deletion Rights",
        'text': "If you're concerned about the data collected, you may have the right to request its deletion. Review the 'User Rights' or 'Your Choices' sections of the policy, or contact the service for details on how to exercise this right.",
        'triggers': [
            {'ai_category': 'User Rights', 'min_concern': ['High', 'Medium']},
            {'ai_category': 'Data Collection', 'min_concern': ['High']},
        ]
    },
    {
        'id': REC_ID_REVIEW_THIRD_PARTY_POLICIES,
        'title': "Review Linked Third-Party Policies",
        'text': "This policy indicates data sharing with third parties. It's advisable to also review the privacy policies of those third parties if they are named or if the sharing seems extensive, as their practices may differ.",
        'triggers': [
            {'ai_category': 'Data Sharing', 'min_concern': ['High', 'Medium']}
        ]
    },
    {
        'id': REC_ID_MONITOR_POLICY_CHANGES,
        'title': "Monitor for Policy Changes",
        'text': "The way this policy handles updates has been noted (or if your preference is to be alerted). Regularly check for updates to their privacy policy, especially if you are concerned about how your data is handled.",
        'triggers': [
            {'ai_category': 'Policy Change', 'min_concern': ['High', 'Medium']}
        ]
    },
    {
        'id': REC_ID_CHILDRENS_PRIVACY_CAUTION,
        'title': "Caution Advised: Children's Privacy",
        'text': "Clauses related to children's privacy have been identified. If this service is used by or collects data from children, pay close attention to these sections and ensure compliance with relevant laws like COPPA (in the US) or similar regulations elsewhere.",
        'triggers': [
            {'ai_category': 'Childrens Privacy', 'min_concern': ['High']}
        ]
    },
    {
        'id': REC_ID_REVIEW_SECURITY_PRACTICES,
        'title': "Review Security Practice Details",
        'text': "The policy mentions security. For sensitive data, consider if the description of security measures meets your expectations or if more clarity is needed from the provider.",
        'triggers': [
            {'ai_category': 'Security', 'min_concern': ['Medium', 'Low']}
        ]
    },
    {
        'id': REC_ID_UNDERSTAND_DATA_RETENTION,
        'title': "Understand Data Retention Periods",
        'text': "The policy discusses data retention. Understand how long your data is kept and for what purposes. If unclear, this might be a point to query with the provider, especially for sensitive information.",
        'triggers': [
            {'ai_category': 'Data Retention', 'min_concern': ['Medium', 'Low']}
        ]
    },
    {
        'id': REC_ID_MANAGE_COOKIES,
        'title': "Manage Your Cookie Preferences",
        'text': "The use of cookies is mentioned. Most browsers allow you to manage cookie settings, and many services offer a cookie consent banner or settings panel to customize your choices for non-essential cookies.",
        'triggers': [
            {'ai_category': 'Cookies and Tracking Technologies', 'min_concern': ['High', 'Medium', 'Low']}
        ]
    }
    # Add more recommendations as needed
]

# Example of how to access a recommendation by ID (optional helper)
def get_recommendation_by_id(rec_id):
    for rec in RECOMMENDATIONS_DATA:
        if rec['id'] == rec_id:
            return rec
    return None

if __name__ == '__main__':
    print(f"Loaded {len(RECOMMENDATIONS_DATA)} recommendations.")
    # Example: Print a specific recommendation
    example_rec = get_recommendation_by_id(REC_ID_OPT_OUT_DATA_SELLING)
    if example_rec:
        print(f"\nExample Recommendation (ID: {example_rec['id']}):")
        print(f"  Title: {example_rec['title']}")
        print(f"  Text: {example_rec['text']}")
        print(f"  Triggers: {example_rec['triggers']}")
