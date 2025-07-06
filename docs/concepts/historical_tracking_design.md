# Design Document: Historical Policy Tracking & Change Alerts

**Version:** 0.1
**Date:** $(date +"%Y-%m-%d")
**Status:** Conceptual

## 1. Introduction

This document outlines the conceptual design for the **Historical Policy Tracking & Change Alerts** feature of the Privacy Protocol project. This capability aims to monitor privacy policies of specified services over time, notify users of significant changes, and allow users to compare versions. This aligns with applying "Prompt Versioning" concepts to legal documents, as mentioned in the README.

## 2. Goals

*   To enable users to track how privacy policies of services they use evolve over time.
*   To automatically detect and highlight changes between different versions of a policy.
*   To alert users to significant or potentially detrimental changes in policies they are tracking.
*   To provide an interface for comparing policy versions side-by-side.

## 3. Core Functionality

### 3.1. Input

*   **URLs of Privacy Policies:** Users will specify the URLs of the policies they wish to track.
*   **User Association:** Track which user is interested in which policy.
*   **(Optional) Frequency of Checks:** Users might be able to suggest how often a policy should be checked for updates (within system limits).

### 3.2. Tracking Process

1.  **Policy Fetching:**
    *   Periodically fetch the content of the specified policy URLs.
    *   Implement polite fetching (respect `robots.txt`, use appropriate User-Agent, manage request frequency to avoid overloading servers).
2.  **Content Storage (`PolicyTracker` module):**
    *   Store each fetched version of the policy text, along with a timestamp and a version identifier.
    *   The `PolicyTracker.policy_history` dictionary (`{ "url1": [{"version": 1, "text": "...", "timestamp": "..."}]}`) is the current placeholder for this.
    *   Consider efficient storage for potentially many versions of many policies (e.g., storing only diffs after the first full version, or using a database).
3.  **Change Detection:**
    *   When a new version of a policy is fetched, compare it to the most recently stored version for that URL.
    *   **Diffing Algorithm:** Employ a text differencing algorithm (e.g., similar to `diff` utility, or more sophisticated semantic diffing) to identify additions, deletions, and modifications.
    *   The current `PolicyTracker.get_policy_changes()` is a placeholder for this.
4.  **Significance Analysis (Future):**
    *   Not all changes are equally important. The system should attempt to determine the significance of detected changes.
    *   This could involve:
        *   Checking if changes occur in sections related to key privacy issues (e.g., data sharing, user rights).
        *   Using NLP to understand the semantic impact of the changes (e.g., a change from "we do not sell your data" to "we may sell your data" is highly significant).
        *   Comparing against a predefined list of "sensitive keywords" or phrases.
5.  **Alerting Users:**
    *   If significant changes are detected, notify the user(s) tracking that policy.
    *   Notification mechanisms: In-app notifications, email alerts (if user accounts and email are implemented).
    *   Alerts should summarize the nature of the change if possible.

### 3.3. Output & User Interface

*   **Change History View:** For a tracked policy, display a list of its versions with timestamps.
*   **Side-by-Side Comparison:** Allow users to select two versions of a policy and view them side-by-side, with differences clearly highlighted (e.g., color-coding for additions/deletions).
*   **Change Summaries:** Provide a concise summary of what has changed between versions.
*   **Notifications:** Clear and actionable alerts about policy updates.

## 4. `PolicyTracker` Module (`privacy_protocol_core/data_tracking/policy_tracker.py`)

*   The `PolicyTracker` class is responsible for storing policy versions and providing basic change detection.
*   `add_policy_version(url, policy_text, timestamp)`
*   `get_policy_changes(url)` (to be enhanced with actual diffing)
*   Future methods: `get_policy_version(url, version_number_or_timestamp)`, `compare_versions(url, version1, version2)`.

## 5. "Prompt Versioning" Analogy

The README mentions "Prompt Versioning" concepts. In this context:
*   **"Prompt" = Privacy Policy:** The legal document is the "prompt" that dictates terms.
*   **"Versioning" = Tracking Changes:** Just as AI engineers version prompts to track changes in model behavior, Privacy Protocol versions policies to track changes in legal terms.
*   **Impact Analysis:** Understanding how changes to the "prompt" (policy) affect the "output" (user rights and data treatment).

## 6. Technical Considerations

*   **Scalability:** Efficiently fetching, storing, and comparing a large number of policies for many users.
*   **Robust URL Fetching:** Handling network errors, redirects, changes in website structure.
*   **Diffing Accuracy:** Choosing or developing a diffing algorithm that accurately highlights meaningful changes in legal text, minimizing noise from formatting changes.
*   **Storage Optimization:** Storing full text of every version can be space-intensive. Consider delta encoding or other compression techniques.
*   **Task Scheduling:** A scheduler (e.g., cron job, Celery for a web app) will be needed to periodically check for policy updates.

## 7. Challenges

*   **Website Structure Changes:** Trackers can break if websites redesign and policy URLs change or content moves.
*   **Dynamic Content:** Some policies might be loaded with JavaScript, requiring more advanced fetching than simple HTTP requests (e.g., using a headless browser).
*   **Determining "Significance":** Automating the assessment of a change's importance is a complex NLP task.
*   **User Interface for Diffs:** Presenting policy differences in a way that is easy to read and understand.

## 8. Future Enhancements

*   **Semantic Diffing:** Go beyond simple text diffs to understand if the meaning of a clause has changed even if the wording is only slightly different.
*   **Subscription Tiers (if applicable):** More frequent checks or tracking of more policies for premium users.
*   **Collaborative Tracking:** Allow users to see if a policy they are interested in is already being tracked and view its history (anonymized if necessary).
*   **RSS/Atom Feeds for Changes:** Provide feeds that users can subscribe to for policy updates.

This feature is crucial for ongoing privacy awareness, as users often agree to a policy once and are unaware of subsequent modifications.
