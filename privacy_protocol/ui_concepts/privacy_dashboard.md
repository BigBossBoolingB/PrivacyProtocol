# Conceptual UI Design: Privacy Risk Dashboard

This document outlines the conceptual user interface (UI) design for the Privacy Protocol's main dashboard. The dashboard aims to provide users with a consolidated, intuitive overview of their privacy posture across all services whose policies they have analyzed.

## 1. Overall Layout & Key Sections

The dashboard will be a single-page view within the application, accessible via a main navigation link (e.g., "Dashboard").

It will be structured with the following key sections:

### 1.1. Overall User Privacy Risk Score (Future)
- **Display:** A prominent, large numerical score (e.g., 0-100, where lower is better, or a qualitative rating like Low/Medium/High Risk).
- **Visualization:** Could be a circular progress bar, a gauge, or color-coded text (Green/Yellow/Red).
- **Context:** A brief explanation of what this overall score represents (e.g., "Your average privacy risk exposure across all analyzed services.").
- **Note:** Calculation of this overall user score (aggregating individual service scores) is a future development.

### 1.2. Key Privacy Insights / Global Alerts (Future)
- **Display:** A small section highlighting 2-3 critical privacy insights or global alerts derived from the user's analyzed policies.
- **Examples:**
    - "Warning: 3 of your analyzed services mention data selling, and you prefer to disallow this."
    - "Insight: Most of your services provide clear opt-out mechanisms for marketing."
    - "Alert: 'Service X' policy changed significantly on [Date]. [Link to view changes]"
- **Note:** Generating these insights automatically is a future development.

### 1.3. List/Grid of Analyzed Services
- **Display:** The main section of the dashboard. Each analyzed service/policy will be represented as a card or a row in a sortable table.
- **Information per Service Card/Row:**
    - **Service Name/Identifier:** (e.g., "Example.com Privacy Policy", "My Social App Terms"). This would ideally be user-editable or derived smartly.
    - **Individual Service Risk Score:** The `service_risk_score` (0-100) calculated for that policy's latest analysis. Displayed numerically and/or with a color code (Green/Yellow/Red).
    - **Last Analyzed Date:** Timestamp of the most recent analysis for that service.
    - **Key Concerns Summary:** 1-2 brief bullet points of the highest concern items for that specific policy (e.g., "Shares data for ads (High Concern)", "Tracks location data (Medium Concern)").
    - **Policy Changed Indicator:** A small icon or text if this policy has changed since the user's last review of it on *this dashboard* or since the last analysis (requires more sophisticated change tracking than just the last diff on `/analyze`).
    - **Action Button/Link:** "View Details" or similar, linking to the detailed analysis view (currently `results.html` via `/history/view/[id]`).
- **Sorting/Filtering (Future):** Allow sorting by service name, risk score, or last analyzed date. Filtering by risk level could also be added.

### 1.4. Quick Actions / Global Recommendations (Future)
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
- Aggregate risk scores and insights from these individual analyses to compute an overall user score and global insights.
- Track policy versions and changes more systematically for each named service to feed into "Policy Changed Indicator" and "Key Privacy Insights".

This conceptual design serves as a blueprint for the future development of the Privacy Risk Dashboard. The initial implementation will focus on enhancing the display of the single-policy risk score on the existing `results.html` page, which serves as a precursor to this more comprehensive dashboard view.
