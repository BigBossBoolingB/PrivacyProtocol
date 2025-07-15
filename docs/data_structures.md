# Data Structures

The Privacy Protocol defines a set of core data structures that are used throughout the framework.

## PrivacyPolicy

The `PrivacyPolicy` class represents a privacy policy. It has the following attributes:

*   `policy_id` (str): A unique identifier for the policy.
*   `version` (int): The version number of the policy.
*   `content` (str): The full text of the policy.
*   `rules` (List[str]): A list of machine-readable rules that are extracted from the policy content.

## UserConsent

The `UserConsent` class represents a user's consent to a specific version of a privacy policy. It has the following attributes:

*   `consent_id` (str): A unique identifier for the consent.
*   `user_id` (str): The ID of the user who has given consent.
*   `policy_id` (str): The ID of the policy to which the user has consented.
*   `policy_version` (int): The version of the policy to which the user has consented.
*   `granted` (bool): A boolean indicating whether consent is currently granted.
*   `timestamp` (datetime.datetime): The timestamp of the last consent action.

## DataAttribute

The `DataAttribute` class represents a single attribute of a user's data. It has the following attributes:

*   `name` (str): The name of the attribute (e.g., "email").
*   `value` (Any): The value of the attribute.
*   `classification` (str): The sensitivity classification of the attribute (e.g., "sensitive").
