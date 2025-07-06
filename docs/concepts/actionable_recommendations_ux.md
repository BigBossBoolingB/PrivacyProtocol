# Design Document: Actionable Recommendations & Opt-Out Navigator (UX Focus)

**Version:** 0.1
**Date:** $(date +"%Y-%m-%d")
**Status:** Conceptual

## 1. Introduction

This document outlines the conceptual design, with a focus on User Experience (UX), for **Actionable Recommendations** and the **Opt-Out Navigator** within the Privacy Protocol project. These features aim to move beyond mere analysis and provide users with concrete steps they can take to manage their privacy based on policy findings and their preferences.

This directly supports the **"Empower Action"** goal of the project vision.

## 2. Goals

*   To provide users with clear, specific, and actionable steps they can take in response to privacy risks or concerns identified in a policy.
*   To simplify the often-convoluted process of finding and using opt-out mechanisms provided by services.
*   To empower users to exercise their data rights (e.g., data deletion requests).
*   To suggest privacy-friendlier alternatives to services where appropriate.
*   To present these actions in an intuitive and easily accessible manner within the application.

## 3. Core Components & UX Flow

### 3.1. `Recommender` Module (`privacy_protocol_core/action_center/recommender.py`)

*   **Functionality:** Generates a list of suggested actions based on policy analysis, risk score, and user profile.
*   **Types of Recommendations:**
    *   **General Advice:** E.g., "Review your settings for this service," "Consider if you need all permissions requested."
    *   **Specific Opt-Outs:** E.g., "This policy mentions targeted advertising. You may be able to opt out here: [Link]."
    *   **Data Deletion Prompts:** E.g., "If you are concerned about the data collected, consider requesting data deletion."
    *   **Alternative Service Suggestions:** E.g., "For [service type, e.g., email], consider these privacy-focused alternatives: [List]."
*   **UX:**
    *   Recommendations should be presented clearly, perhaps as a list or cards, after a policy is analyzed.
    *   Each recommendation should be concise and start with an action verb.
    *   Prioritize recommendations based on severity or user preferences.

### 3.2. `OptOutNavigator` Module (`privacy_protocol_core/action_center/opt_out_navigator.py`)

*   **Functionality:**
    *   Maintains a database/knowledge base of direct links to privacy settings and opt-out pages for various online services. (Placeholder: `self.opt_out_links` dictionary).
    *   Provides pre-filled email templates for common data rights requests (e.g., data deletion, data access). (Placeholder: `self.deletion_templates` dictionary).
*   **UX for Direct Links:**
    *   When a service is identified (e.g., from the policy URL or user input), the system should check if a direct opt-out or privacy settings link is known.
    *   If available, present this as a clear "Go to Privacy Settings" or "Opt-Out Here" button/link.
    *   **Deep Linking (Ideal):** If possible, link directly to the relevant section of the service's settings, not just the homepage.
    *   **Community Sourcing (Future):** Consider mechanisms for users to submit and verify opt-out links.
*   **UX for Email Templates:**
    *   If a user wishes to request data deletion or access:
        *   Select the type of request.
        *   The system provides a template.
        *   Pre-fill known information (e.g., service name, user name if available from profile).
        *   Allow the user to copy the template or (future) directly open it in their email client.
        *   Provide guidance on where to send the request (e.g., common DPO email addresses, support contacts).

## 4. User Experience Journey Example

1.  **Policy Analysis:** User submits a privacy policy for analysis.
2.  **Results Display:** The system shows the risk score, interpreted clauses, and "What If" scenarios.
3.  **Action Center Section:** Prominently displayed alongside or below the analysis results is an "Action Center" or "Next Steps" section.
    *   **Contextual Recommendations:** The `Recommender` populates this section.
        *   *"Based on this policy's high risk score (85/100) and its mention of data selling, we recommend:"*
            *   *"[Button/Link] Opt-Out of Data Selling (if known link exists via OptOutNavigator)"*
            *   *"[Action] Review your account settings on [Service Name] for data sharing options."*
            *   *"[Action] Consider requesting data deletion if you no longer use this service. [Link to generate deletion email template]"*
    *   **Alternative Suggestions:**
        *   *"Looking for alternatives to [Service Type]? Consider: [Link to ProtonMail], [Link to Tutanota]."*
4.  **Using the Opt-Out Navigator:**
    *   Clicking an opt-out link takes the user (ideally in a new tab) to the service's page.
    *   Clicking "Generate deletion email" would:
        *   Open a modal or new view.
        *   Display the `OptOutNavigator`-provided template.
        *   Allow the user to fill in any remaining placeholders (e.g., their account username for that service).
        *   Offer a "Copy to Clipboard" button.
        *   Provide information on where to typically send such requests for [Service Name].

## 5. Key UI Elements (Conceptual)

*   **Actionable Cards/List Items:** Each recommendation or opt-out option presented clearly.
*   **Clear Call-to-Action (CTA) Buttons:** "Opt-Out," "Copy Email," "Go to Settings."
*   **Tooltips/Info Icons:** Provide more context for recommendations or why a certain action is suggested.
*   **Progress Tracking (Future):** Allow users to mark actions as "taken" or "to-do."
*   **Searchable Knowledge Base (Future):** Users could search directly for opt-out information for a specific service.

## 6. Challenges and Considerations

*   **Maintaining Opt-Out Links:** These links change frequently as websites are updated. Keeping the `OptOutNavigator`'s database current is a significant challenge. This is a prime area for community contributions or automated link checking.
*   **Complexity of Opt-Out Processes:** Some services make opting out intentionally difficult. The navigator can simplify finding the starting point, but the user still has to navigate the service's interface.
*   **Effectiveness of Requests:** Sending a data deletion email doesn't guarantee the company will comply promptly or fully. The system can empower the request, but not enforce it.
*   **User Trust:** Users need to trust that the links are legitimate and the email templates are effective.
*   **Localization:** Templates and guidance may need to be adapted for different languages and legal jurisdictions.

## 7. Future Enhancements

*   **Browser Extensions:** A companion browser extension could detect the current website and proactively offer opt-out links or context-aware advice.
*   **Automated Form Filling (with caution and consent):** For common opt-out forms, explore possibilities of assisting with form completion.
*   **Tracking Request Status:** Allow users to manually track the status of data deletion/access requests they've sent.
*   **Integration with "Do Not Sell" Signals (e.g., Global Privacy Control):** Help users enable such browser-level signals.

By focusing on clear, actionable steps and simplifying complex processes, the Actionable Recommendations and Opt-Out Navigator can be key features in empowering users to actively manage their privacy.
