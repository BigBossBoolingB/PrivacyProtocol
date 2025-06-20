# Privacy Protocol: Machine Learning Model Integration Roadmap

This document outlines the path from the current placeholder (dummy) AI clause classifier to a fully trained machine learning model for categorizing privacy policy clauses, and the integration of generative AI for plain-language summaries. The goal is to enhance the accuracy and depth of analysis provided by the Privacy Protocol application.

## External API Integrations

This section details the use of external AI services to enhance the capabilities of Privacy Protocol. The application uses an `LLMServiceFactory` to select and instantiate a configured LLM provider based on the `ACTIVE_LLM_PROVIDER` environment variable. Supported providers are "gemini", "openai", "anthropic", and "azure_openai".

### Gemini Pro API for Plain Language Translation
- **Service Used:** Google's Gemini Pro API.
- **Purpose:** To translate complex legal jargon from policy clauses into simple, clear terms.
- **API Key Configuration:**
    - Requires an API key from Google AI Studio.
    - Set as an environment variable named `GEMINI_API_KEY`.
    - Refer to `.env.example` and the main `README.md` for setup instructions.
- **Client Module:** `privacy_protocol/privacy_protocol/llm_services/gemini_api_client.py` (as `GeminiLLMService`).
- **Fallback:** If the API key is not configured or API calls fail, the system falls back to predefined dummy explanations.

### OpenAI (GPT models) for Plain Language Translation
- **Service Used:** OpenAI's GPT models (e.g., gpt-3.5-turbo).
- **Purpose:** Alternative provider for generating plain-language summaries.
- **API Key Configuration:**
    - Requires an API key from OpenAI.
    - Set as an environment variable named `OPENAI_API_KEY`.
    - Refer to `.env.example` and the main `README.md`.
- **Client Module:** `privacy_protocol/privacy_protocol/llm_services/openai_api_client.py` (as `OpenAILLMService`).
- **Fallback:** Uses dummy explanations if the API key is missing or calls fail.

### Anthropic (Claude models) for Plain Language Translation
- **Service Used:** Anthropic's Claude models (e.g., claude-3-sonnet).
- **Purpose:** Alternative provider for generating plain-language summaries.
- **API Key Configuration:**
    - Requires an API key from Anthropic.
    - Set as an environment variable named `ANTHROPIC_API_KEY`.
    - Refer to `.env.example` and the main `README.md`.
- **Client Module:** `privacy_protocol/privacy_protocol/llm_services/anthropic_api_client.py` (as `AnthropicLLMService`).
- **Fallback:** Uses dummy explanations if the API key is missing or calls fail.

### Microsoft Azure OpenAI Service
- **Service Used:** OpenAI models deployed via Microsoft Azure OpenAI Service.
- **Purpose:** Enterprise-grade alternative for generating plain-language summaries using OpenAI models.
- **API Key Configuration:**
    - Requires an API key, endpoint URL, deployment name, and API version from an Azure OpenAI resource.
    - Set as environment variables: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT_NAME`, `AZURE_OPENAI_API_VERSION`.
    - Refer to `.env.example` and the main `README.md`.
- **Client Module:** `privacy_protocol/privacy_protocol/llm_services/azure_openai_client.py` (as `AzureOpenAILLMService`).
- **Fallback:** Uses dummy explanations if configurations are missing or calls fail.

## Clause Classification: From Dummy to Trained Model

### Current State: Dummy Classifier

The application currently uses a `ClauseClassifier` located in `privacy_protocol/privacy_protocol/ml_classifier.py`. This is a **placeholder/dummy classifier** that operates based on a predefined set of rules using simple keyword and regex matching.

**Purpose of the Dummy Classifier:**
- To establish the software architecture for integrating an ML model for clause categorization.
- To define the expected input (clause text) and output (a category string) for this classification component.
- To allow the rest of the application (interpreter, web interface, tests) to be built and tested with a consistent AI component interface for categorization.

**Limitations of the Dummy Classifier:**
- **Accuracy:** Relies on manually curated keywords and simple rules.
- **Scalability:** Manually adding rules for every possible phrasing is not sustainable.
- **Generalization:** Poor at handling unseen phrasings.

### Defined Clause Categories

The target categories for clause classification are currently defined in `privacy_protocol/privacy_protocol/clause_categories.py`. (List of categories as previously present).

This list may evolve as the project matures.

### Roadmap to a Trained ML Model for Clause Classification

Replacing the dummy classifier with a trained ML model involves several key phases: (Details for phases 1-7 remain largely the same as previously listed: Data Collection, Annotation, Model Selection, Training, Evaluation, Serialization/Integration, Iteration).

### Considerations for Clause Classification Model
- **Computational Resources:** Training large transformer models can be computationally intensive.
- **Dataset Bias:** The model will learn biases present in the training data.
- **Interpretability:** Understanding model predictions can be challenging but important.

This roadmap provides a high-level guide for developing a robust AI-powered clause classifier.

## Plain-Language Translation: Strategy and Development
*(Note: The primary approach for plain-language translation is now through configurable external LLM APIs (Gemini, OpenAI, Anthropic, Azure OpenAI) managed by the `LLMServiceFactory` and utilized by `PlainLanguageTranslator`. The original notes below on training a custom sequence-to-sequence model are kept for long-term reference or as an alternative strategy if direct API use becomes infeasible or if highly specialized custom fine-tuning proves necessary beyond what current APIs offer.)*

### Current State: `PlainLanguageTranslator` with External API Integration

The application includes a `PlainLanguageTranslator` in `privacy_protocol/privacy_protocol/plain_language_translator.py`.
**Functionality:**
- This component utilizes the `LLMServiceFactory` to obtain a configured LLM service instance (e.g., `GeminiLLMService`, `OpenAILLMService`, `AnthropicLLMService`, `AzureOpenAILLMService`).
- It attempts to call the selected LLM service to generate plain-language summaries for input clauses. The AI category of the clause is used to provide context to the generative model via a structured prompt.
- If the selected LLM service's API key (or all necessary configurations for Azure) is not configured, or if an API call fails, the translator falls back to providing predefined, category-based dummy explanations.

**Limitations of the Fallback Dummy Explanations:**
- **Generic Summaries:** The fallback summaries are category-based, not tailored to the specific content of the individual clause.
- **Not Data-Driven:** Fallback explanations are hardcoded.

### Roadmap to a Custom Trained AI Translation/Summarization Model (Alternative Strategy)

Replacing or supplementing the external APIs with a custom-trained AI model (typically a sequence-to-sequence model) would involve: (Details for phases 1-6 remain largely the same as previously listed: Parallel Corpus Collection, Model Selection, Training/Fine-tuning, Evaluation, Serialization/Integration, Iteration).

Developing a high-quality custom AI plain-language translator is a significant undertaking, with data collection for a parallel corpus being a primary challenge. The current multi-provider API integration offers flexibility and access to powerful existing models.

## Service Risk Scoring Algorithm

The application calculates a `service_risk_score` (normalized 0-100) for each analyzed privacy policy to provide an at-a-glance understanding of its potential risk based on the current analysis and user preferences.

### Inputs to the Score:
-   **AI-Predicted Category (`ai_category`):** The category assigned to each clause by the clause classifier (currently rule-based, planned to be LLM-driven).
-   **User Concern Level (`user_concern_level`):** 'High', 'Medium', 'Low', or 'None', determined by comparing the `ai_category` (and potentially keywords) against user-defined preferences.

### Calculation Steps:

1.  **Base Points per AI Category:** Each `ai_category` has predefined base risk points:
    -   'Data Selling': 20
    -   'Data Sharing': 15
    -   'Cookies and Tracking Technologies': 10
    -   'Childrens Privacy': 15
    -   'Data Collection': 10
    -   'Security': 0 (Neutral by default)
    -   'Data Retention': 5
    -   'Policy Change': 5
    -   'User Rights': 10
    -   'International Data Transfer': 5
    -   'Contact Information': 0
    -   'Consent/Opt-out': 10
    -   'Other': 1

2.  **Bonus Points per User Concern Level:**
    -   'High' concern: +15 points
    -   'Medium' concern: +7 points
    -   'Low' concern: +2 points
    -   'None' concern: +0 points

3.  **Per-Sentence Risk:** For each analyzed sentence:
    `sentence_risk = AI_CATEGORY_BASE_POINTS[sentence.ai_category] + USER_CONCERN_BONUS_POINTS[sentence.user_concern_level]`

4.  **Total Accumulated Risk:** Sum of all `sentence_risk` values.

5.  **Normalization:**
    -   `MAX_RISK_POINTS_PER_SENTENCE` is calculated as `max(AI_CATEGORY_BASE_POINTS.values()) + USER_CONCERN_BONUS_POINTS['High']` (e.g., 20 + 15 = 35).
    -   `total_possible_risk = num_clauses_analyzed * MAX_RISK_POINTS_PER_SENTENCE`.
    -   `service_risk_score = (total_accumulated_risk / total_possible_risk) * 100` (if `total_possible_risk > 0`, else 0).
    -   The score is then rounded and capped between 0 and 100.

This initial algorithm provides a quantitative measure. Future enhancements may involve more dynamic weighting or machine-learned risk models.
