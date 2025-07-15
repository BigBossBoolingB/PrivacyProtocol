# Enforcement Engine

The Enforcement Engine is the heart of the Privacy Protocol. It is responsible for processing data according to user consent and the governing privacy policy.

## Components

The Enforcement Engine consists of three main components:

*   **DataClassifier:** This component is responsible for classifying data based on its sensitivity. It uses a machine learning model to automatically classify data, but it can also be configured with a set of rules for manual classification.
*   **PolicyEvaluator:** This component is responsible for evaluating data processing requests against user consent and the governing privacy policy. It uses a rule-based engine to determine whether a request is permitted.
*   **ObfuscationEngine:** This component is responsible for obfuscating sensitive data. It supports a variety of obfuscation techniques, including redaction, substitution, and generalization.

## PrivacyEnforcer

The `PrivacyEnforcer` is the central orchestrator of the Enforcement Engine. It ties all the other components together to provide a seamless and comprehensive privacy enforcement solution. It takes a data processing request as input, and it returns a processed data record with a privacy status.
