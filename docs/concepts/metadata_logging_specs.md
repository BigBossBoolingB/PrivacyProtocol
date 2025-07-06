# Design Document: Metadata Logging Specifications

**Version:** 0.1
**Date:** $(date +"%Y-%m-%d")
**Status:** Conceptual

## 1. Introduction

This document specifies the design for **Metadata Logging** within the Privacy Protocol project. As stated in the README, the system will internally log key data points about content origins and policy interactions. This logging serves multiple purposes: supporting future authenticity initiatives, debugging, understanding user interaction patterns (anonymized and aggregated), and potentially providing users with a history of their activity.

## 2. Goals

*   To create a structured and consistent way of logging important events and data points within the application.
*   To ensure that logged metadata is useful for future analysis, debugging, and potential feature enhancements (like user activity history or authenticity checks).
*   To define the scope of what should be logged, keeping user privacy in mind (i.e., not logging sensitive policy text itself in general logs unless explicitly for history/cache).
*   To provide a foundation for understanding how users interact with the system and which features are most used/effective.

## 3. `MetadataLogger` Module (`privacy_protocol_core/data_tracking/metadata_logger.py`)

*   The `MetadataLogger` class is the central component for this functionality.
*   **Current Implementation:**
    *   `log_entries`: Stores log entries in a list in memory.
    *   `log_interaction(user_id, policy_url, action, details=None)`: Creates a log entry with a timestamp, user ID, policy URL, a defined action, and optional structured details.
    *   `get_logs_for_user(user_id)`: Retrieves logs for a specific user.

## 4. Logged Events and Data Points

The following are examples of events and associated metadata that should be logged. The `action` field in `log_interaction` will be a key enum/string.

### 4.1. Policy Analysis Events

*   **Action:** `POLICY_ANALYSIS_REQUESTED`
    *   `user_id`: Identifier of the user initiating the analysis.
    *   `policy_url`: The URL of the policy being analyzed (if provided).
    *   `policy_source`: (e.g., "url", "text_input")
    *   `timestamp`: Time of request.
*   **Action:** `POLICY_ANALYSIS_COMPLETED`
    *   `user_id`: User identifier.
    *   `policy_url`: Policy URL.
    *   `timestamp`: Time of completion.
    *   `details`:
        *   `risk_score_generated`: The calculated risk score.
        *   `clauses_identified`: Count of disagreeable/questionable clauses found.
        *   `processing_time_ms`: Duration of the analysis.
*   **Action:** `POLICY_ANALYSIS_FAILED`
    *   `user_id`: User identifier.
    *   `policy_url`: Policy URL.
    *   `timestamp`: Time of failure.
    *   `details`:
        *   `error_type`: (e.g., "fetch_error", "parsing_error", "analysis_error")
        *   `error_message`: Brief error description.

### 4.2. User Profile Events

*   **Action:** `USER_PROFILE_CREATED`
    *   `user_id`: The ID of the newly created profile.
    *   `timestamp`: Time of creation.
    *   `details`: (Optional) Initial settings or source of creation.
*   **Action:** `USER_PROFILE_UPDATED`
    *   `user_id`: User identifier.
    *   `timestamp`: Time of update.
    *   `details`:
        *   `updated_fields`: List of fields that were changed (e.g., ["privacy_tolerance.data_sharing", "custom_alerts"]).
        *   `previous_values`: (Optional, for detailed auditing, consider privacy implications) Key-value pairs of previous settings.

### 4.3. Action Center Events

*   **Action:** `RECOMMENDATION_DISPLAYED`
    *   `user_id`: User identifier.
    *   `policy_url`: Associated policy URL.
    *   `timestamp`: Time recommendations were shown.
    *   `details`:
        *   `recommendation_count`: Number of recommendations shown.
        *   `recommendation_types`: List of types of recommendations (e.g., ["opt_out_link", "deletion_template_prompt"]).
*   **Action:** `OPT_OUT_LINK_CLICKED`
    *   `user_id`: User identifier.
    *   `policy_url`: Associated policy URL (or service name).
    *   `opt_out_url_provided`: The URL the user was directed to.
    *   `timestamp`: Time of click.
*   **Action:** `DELETION_TEMPLATE_GENERATED`
    *   `user_id`: User identifier.
    *   `service_name`: Service for which the template was generated.
    *   `timestamp`: Time of generation.

### 4.4. Policy Tracking Events (from `PolicyTracker` interactions)

*   **Action:** `POLICY_ADDED_TO_TRACKER`
    *   `user_id`: User who initiated tracking (or "system" if automated).
    *   `policy_url`: URL of the policy added.
    *   `timestamp`: Time of addition.
*   **Action:** `POLICY_VERSION_FETCHED`
    *   `policy_url`: URL of the policy.
    *   `timestamp`: Time of fetch.
    *   `details`:
        *   `fetch_status`: ("success", "failure")
        *   `content_hash`: Hash of the fetched content (to detect changes without storing full text in this specific log).
        *   `version_number_assigned`: Version ID in `PolicyTracker`.
*   **Action:** `POLICY_CHANGE_DETECTED`
    *   `policy_url`: URL of the policy.
    *   `timestamp`: Time change was detected.
    *   `details`:
        *   `previous_version`: Identifier of the previous version.
        *   `new_version`: Identifier of the new version.
        *   `change_summary_type`: (e.g., "diff_available", "significant_change_flagged") - more detail needed as feature evolves.
*   **Action:** `USER_ALERTED_POLICY_CHANGE`
    *   `user_id`: User identifier.
    *   `policy_url`: URL of the policy.
    *   `timestamp`: Time of alert.
    *   `details`:
        *   `alert_method`: (e.g., "in_app", "email")

## 5. Log Storage and Management

*   **Initial:** In-memory list (`self.log_entries` in `MetadataLogger`). Suitable for single sessions and basic testing.
*   **Short-term Improvement:** Log to a local file (e.g., `privacy_protocol.log` as mentioned in `config.py`). This file could be rotated.
*   **Long-term (Server-Side Application):**
    *   **Database:** Store logs in a structured database (SQL or NoSQL like Elasticsearch/MongoDB) for querying and analysis. This allows for persistence, aggregation, and easier management.
    *   **Log Management System:** Use dedicated logging services (e.g., ELK stack, Splunk, cloud-based logging services) for collection, searching, and visualization.

## 6. Privacy Considerations for Logging

*   **Anonymization/Pseudonymization:** For aggregated analytics, ensure `user_id` is pseudonymized or data is fully anonymized.
*   **Sensitive Data:** Avoid logging full policy texts or user-inputted sensitive information directly in general metadata logs. The `PolicyTracker` stores policy text for its specific purpose, but general logs should reference it by URL/ID.
*   **Log Retention Policies:** Define how long logs are kept, especially if they contain user identifiers.
*   **User Access to Their Logs (Future):** Consider allowing users to view a history of their own interactions with Privacy Protocol, which would be derived from these logs.

## 7. Authenticity Initiatives (Future)

The logged metadata can support future "authenticity initiatives" by:
*   Providing a trail of when a policy was fetched and what its hash was, which could be used to verify if a presented policy matches what was seen at a certain time.
*   Tracking the provenance of interpretations (e.g., which version of the interpreter logic was used).
*   If integrated with external timestamping authorities or blockchain (highly conceptual), logs could provide stronger proof of existence/content at a point in time.

## 8. Structure of `details` Field

The `details` field in `log_interaction` should be a JSON-serializable dictionary (or Python dict) to allow for structured querying and flexibility in what information is captured for different event types.

## 9. Log Levels

While `MetadataLogger` is for specific interaction events, general application logging (debug, info, error, warning) should use Python's standard `logging` module, configured via `config.py`. `MetadataLogger` events are typically at an "INFO" or "AUDIT" level.

This specification provides a baseline. The exact events and details logged will evolve with the application's features.
