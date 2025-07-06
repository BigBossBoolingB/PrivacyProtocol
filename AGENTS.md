# AGENTS.md for PrivacyProtocol (Root Level)

This document provides guidance for AI agents contributing to the PrivacyProtocol project.

## Core Mission Understanding

*   **Primary Goal:** To build a system that demystifies privacy agreements, highlights risks, and empowers users to control their personal data.
*   **Guiding Philosophy:** Adhere to Josephis K. Wade's **Expanded KISS Principle** as outlined in the `README.md`. All development choices should reflect this philosophy.
    *   **K (Know Your Core, Keep it Clear):** Focus on clarity in analysis and output.
    *   **I (Iterate Intelligently, Integrate Intuitively):** Design for adaptability and user-friendliness.
    *   **S (Systematize for Scalability, Synchronize for Synergy):** Build robust, interconnected tools.
    *   **S (Sense the Landscape, Secure the Solution):** Proactively identify and address privacy risks.
    *   **S (Stimulate Engagement, Sustain Impact):** Create intuitive and empowering user experiences.

## Development Guidelines

1.  **Modularity:** Design components to be as modular and reusable as possible. The core modules (interpretation, user_management, risk_assessment, etc.) should have clear responsibilities and interfaces.
2.  **Test-Driven Development (TDD):** Where practical, write tests *before* implementing new functionality. All new code should be accompanied by corresponding unit tests.
    *   Use the `unittest` framework for now. Test files should mirror the structure of the `privacy_protocol_core` directory within the `tests` directory.
    *   Ensure all tests pass before submitting changes.
3.  **Code Clarity and Readability:**
    *   Follow PEP 8 guidelines for Python code.
    *   Write clear and concise comments, especially for complex logic.
    *   Use meaningful variable and function names.
    *   Include docstrings for all modules, classes, and functions, explaining their purpose, arguments, and return values.
4.  **Configuration Management:**
    *   Store configurable parameters (e.g., API keys, model names, thresholds) in `privacy_protocol_core/config.py`.
    *   Avoid hardcoding sensitive information or environment-specific paths directly into functional code.
5.  **Error Handling:** Implement robust error handling. Anticipate potential issues (e.g., network errors if fetching policies, malformed input) and handle them gracefully.
6.  **Logging:** Utilize the `MetadataLogger` for tracking user interactions and policy analysis events as specified in its design. For general application logging (debugging, info, errors), use Python's built-in `logging` module, configured via `privacy_protocol_core/config.py`.
7.  **Security:** Be mindful of security implications, especially when handling user data or interacting with external services. (Specific security guidelines will be added as the project matures).
8.  **Dependencies:** Add new dependencies to `requirements.txt` and provide justification if the dependency is not common.
9.  **README and Documentation:**
    *   If your changes impact the project structure, setup, or usage, update `README.md` accordingly.
    *   For significant new features or architectural changes, contribute to relevant documents in `docs/concepts/`.

## Specific Tasks & Considerations

*   **NLP Integration (Future):** When integrating NLP models for clause interpretation and risk identification:
    *   Prioritize models that can run locally or have clear privacy policies themselves if using cloud-based APIs.
    *   Consider the "AI Humanization" principle – outputs should be understandable to non-experts.
    *   Think about "Prompt Versioning" concepts when designing how the system interacts with policies that change over time.
*   **"What If" Scenarios (Future):** This feature will require creative AI. Focus on generating plausible and informative scenarios based on policy text.
*   **Placeholder Code:** When implementing features based on the initial placeholder files:
    *   Replace `TODO` comments with actual logic.
    *   Expand basic class structures with necessary methods and attributes.
    *   Flesh out the example usage in `privacy_protocol_core/main.py` as features become functional.

## Plan Adherence

*   Follow the established plan provided by the user or lead developer.
*   If a plan step is unclear or needs modification, request clarification or suggest a revision using the appropriate tools.
*   Mark plan steps as complete only when all sub-tasks for that step are verifiably done.

## Communication

*   Provide clear commit messages summarizing the changes made.
*   When submitting code, briefly explain the purpose of the changes and how they address the relevant issue or plan step.

By adhering to these guidelines, AI agents can significantly contribute to the success and integrity of the PrivacyProtocol project. This document may be updated as the project evolves.
