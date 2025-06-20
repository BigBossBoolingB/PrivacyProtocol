# Conceptual UI Design: Privacy Risk Dashboard

This document outlines the conceptual user interface (UI) design for the Privacy Protocol's main dashboard. The dashboard aims to provide users with a consolidated, intuitive overview of their privacy posture across all services whose policies they have analyzed.

## 1. Overall Layout & Key Sections

The dashboard will be a single-page view within the application, accessible via a main navigation link (e.g., "Dashboard").

It will be structured with the following key sections:

### 1.1. Overall User Privacy Risk Score
- **Status:** Implemented (Initial Version)
- **Display:** A prominent, large numerical score (0-100), color-coded (Green/Yellow/Red) for Low/Medium/High risk.
- **Context:** Represents an average privacy risk exposure across all analyzed services. Accompanied by counts of services in high, medium, and low risk categories, and the total number of services analyzed. Last aggregation timestamp is shown.
- **Future Enhancements:** Weighted averaging, more sophisticated risk aggregation beyond a simple average.

### 1.2. Key Privacy Insights / Global Alerts
- **Status:** Implemented (Basic Version)
- **Display:** A section highlighting a few key privacy insights derived from the user's analyzed policies.
- **Current Implementation:** Shows generic insights if specific high-risk patterns are detected (e.g., "Service X has a High privacy risk score"). If no specific patterns, shows a general statement based on overall score. Limited to a few insights.
- **Future Enhancements:** More sophisticated, context-aware insights (e.g., "3 services engage in data selling, and you prefer to disallow this."), alerts for significant policy changes across services.

### 1.3. List/Grid of Analyzed Services
- **Status:** Implemented
- **Display:** The main section of the dashboard. Each analyzed service/policy is represented as a card.
- **Information per Service Card/Row:**
    - **Service Name/Identifier:** Derived from URL or policy identifier for pasted text.
    - **Individual Service Risk Score:** The `service_risk_score` (0-100) for that policy's latest analysis, color-coded.
    - **Last Analyzed Date:** Timestamp of the most recent analysis.
    - **Action Button/Link:** "View Details" linking to the detailed historical analysis view (`/history/view/[id]`).
- **Sorting:** Default sort is by last analyzed timestamp (most recent first).
- **Future Enhancements:**
    - User-editable service names.
    - More detailed "Key Concerns Summary" per service card.
    - "Policy Changed Indicator" (requires more advanced change tracking).
    - Advanced sorting and filtering options.

### 1.4. Quick Actions / Global Recommendations (Future)
- **Status:** Future
- **Display:** A section for general privacy tips or quick actions not tied to a specific policy.
- **Examples:**
    - "Review your device's global ad tracking settings."
    - "Consider using a password manager."
    - Link to global opt-out sites (e.g., NAI, DAA).

## 2. Navigation & Drill-Down

- **From Service Card to Detailed View:** Clicking "View Details" on a service card will navigate the user to the detailed analysis results page for that specific policy version (currently, this would be the `/history/view/[policy_identifier]` route, displaying `results.html`).
- **From Detailed View back to Dashboard:** The detailed view page should have a clear link back to the main Dashboard.
- **Access to Preferences:** A clear link to the `/preferences` page should be available from the dashboard or main app navigation.

## 3. Visual Design Principles

- **Clarity:** Prioritize clear, easy-to-understand information. Avoid jargon where possible.
- **Actionability:** Guide users towards understanding their risks and potential actions.
- **Visual Cues:** Use color-coding (Green/Yellow/Red for risk levels), icons, and clear typography to enhance readability and quickly convey status.
- **Responsiveness (Future):** The dashboard should ideally be designed to work well on various screen sizes.

## 4. Data Requirements (for future full implementation)

To fully realize this dashboard, the backend will need to:
- Store and retrieve multiple named/identified policy analyses per user.
- The implemented version aggregates `service_risk_score` for an overall score and provides basic insights.
- More sophisticated tracking of policy versions and changes for indicators/alerts is a future enhancement.

This document has been updated to reflect the initial implemented version of the Privacy Risk Dashboard. Further iterations will build upon this foundation.
