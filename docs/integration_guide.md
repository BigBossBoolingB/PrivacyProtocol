# Privacy Protocol Integration Guide

This guide provides instructions for integrating the Privacy Protocol framework into your own projects.

## Installation

To install the Privacy Protocol as a library, navigate to the project's root directory and use pip:

```bash
pip install .
```

This will install the `privacy_protocol` package and its dependencies.

## Initializing Core Components

The main components of the Privacy Protocol are designed to be used together. Here's how you can initialize them:

```python
from privacy_protocol import (
    PolicyStore,
    ConsentStore,
    ConsentManager,
    DataTransformationAuditor,
    PrivacyEnforcer,
)

# 1. Initialize the storage components
policy_store = PolicyStore(storage_path="_data/policies/")
consent_store = ConsentStore(storage_path="_data/consents/")

# 2. Initialize the managers and auditors
consent_manager = ConsentManager(consent_store)
auditor = DataTransformationAuditor(log_file_path="_data/audit_log.jsonl")

# 3. Initialize the main enforcer
enforcer = PrivacyEnforcer(policy_store, consent_manager, auditor)
```

## Common Integration Patterns

### Processing a Data Stream

The primary use case for the Privacy Protocol is to process a stream of data and apply privacy rules based on user consent.

```python
# Assume 'enforcer' is initialized as shown above
# Assume a policy and consent have been saved

user_id = "user_123"
policy_id = "your_policy_id"
data_record = {"name": "Jane Doe", "email": "jane.doe@example.com", "purchase_history": [...]}

# Process the data for a specific purpose
processed_data = enforcer.process_data_stream(
    user_id=user_id,
    policy_id=policy_id,
    data_record=data_record,
    intended_purpose="Analytics"
)

print(f"Privacy Status: {processed_data['privacy_status']}")
print(f"Processed Record: {processed_data}")
```

### Managing User Consent

You can programmatically grant and revoke user consent.

```python
# Grant consent
consent_manager.grant_consent(
    user_id="user_123",
    policy_id="your_policy_id",
    policy_version=1
)

# Check for consent
has_consent = consent_manager.has_consent("user_123", "your_policy_id")

# Revoke consent
consent_manager.revoke_consent("user_123", "your_policy_id")
```

### Handling Audit Logs

The `DataTransformationAuditor` creates a tamper-evident log of all data processing events. You can read this log to audit privacy compliance.

```python
import json

with open(auditor.log_file_path, "r") as f:
    for line in f:
        log_entry = json.loads(line)
        # Process the log entry
```

## Public API Components

The following components are part of the public API:

- `PrivacyPolicy`: Represents a privacy policy.
- `UserConsent`: Represents a user's consent.
- `PolicyStore`: Manages storage for privacy policies.
- `ConsentStore`: Manages storage for user consent.
- `ConsentManager`: Manages the logic for granting and revoking consent.
- `DataClassifier`: Classifies data based on sensitivity.
- `ObfuscationEngine`: Obfuscates data based on classification.
- `PolicyEvaluator`: Evaluates if a purpose is permitted by a policy.
- `PrivacyEnforcer`: The main orchestrator for the privacy framework.
- `DataTransformationAuditor`: Logs all data transformations.
- `PrivacyPolicyVerifier`: A conceptual module for formal policy verification.

## Managing Data Directories

The `PolicyStore`, `ConsentStore`, and `DataTransformationAuditor` all write data to disk. By default, they use a `_data/` directory. It is recommended to add this directory to your `.gitignore` file to avoid committing sensitive user data to your repository.
