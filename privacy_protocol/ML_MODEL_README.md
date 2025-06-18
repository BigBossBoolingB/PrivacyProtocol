# Privacy Protocol: Machine Learning Model Integration Roadmap

This document outlines the path from the current placeholder (dummy) AI clause classifier to a fully trained machine learning model for categorizing privacy policy clauses, and the integration of generative AI for plain-language summaries. The goal is to enhance the accuracy and depth of analysis provided by the Privacy Protocol application.

## External API Integrations

This section details the use of external AI services to enhance the capabilities of Privacy Protocol.

### Gemini Pro API for Plain Language Translation
- **Service Used:** The application leverages the Gemini Pro API (from Google) to generate plain language summaries of privacy policy clauses.
- **Purpose:** To translate complex legal jargon from policy clauses into simple, clear terms understandable by a general audience.
- **API Key Configuration:**
    - To use this feature, you must obtain an API key from Google AI Studio (or Google Cloud Vertex AI if using it within that ecosystem).
    - The API key must be set as an environment variable named `GEMINI_API_KEY`.
    - You can set this variable in your shell (e.g., `export GEMINI_API_KEY="your_key_here"`) or by creating a `.env` file in the project root (`privacy_protocol/`) and placing the key there (e.g., `GEMINI_API_KEY="your_key_here"`). Refer to `.env.example`.
    - Ensure the `.env` file is listed in `.gitignore` to prevent accidental commitment of the key.
- **Client Module:** The `privacy_protocol/privacy_protocol/gemini_api_client.py` module handles communication with the Gemini API.
- **Fallback Mechanism:** If the `GEMINI_API_KEY` is not configured, or if the API call fails (e.g., network issues, rate limits, content safety blocks), the `PlainLanguageTranslator` will fall back to providing predefined, category-based dummy explanations. This ensures basic functionality even if the generative AI service is unavailable.

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

The target categories for clause classification are currently defined in `privacy_protocol/privacy_protocol/clause_categories.py`. As of this writing, they include:

- Data Collection
- Data Sharing
- Data Usage
- User Rights
- Security
- Data Retention
- Consent/Opt-out
- Policy Change
- International Data Transfer
- Childrens Privacy
- Contact Information
- Cookies and Tracking Technologies
- Data Selling
- Other (default/fallback)

This list may evolve as the project matures.

### Roadmap to a Trained ML Model for Clause Classification

Replacing the dummy classifier with a trained ML model involves several key phases:

1.  **Data Collection and Preparation** (Details as previously listed)
2.  **Data Annotation** (Details as previously listed)
3.  **Model Selection and Architecture** (Details as previously listed)
4.  **Model Training** (Details as previously listed)
5.  **Model Evaluation** (Details as previously listed)
6.  **Model Serialization and Integration** (Details as previously listed)
7.  **Iteration and Improvement** (Details as previously listed)

### Considerations for Clause Classification Model
- **Computational Resources:** Training large transformer models can be computationally intensive.
- **Dataset Bias:** The model will learn biases present in the training data.
- **Interpretability:** Understanding model predictions can be challenging but important.

This roadmap provides a high-level guide for developing a robust AI-powered clause classifier.

## Plain-Language Translation Model Development
*(Note: The primary approach for plain-language translation has shifted to using the Gemini Pro API as described in the "External API Integrations" section. The following details regarding training a custom sequence-to-sequence model are kept for long-term reference or as an alternative strategy if direct API use becomes infeasible or if highly specialized custom fine-tuning is required.)*

### Current State: `PlainLanguageTranslator` with Gemini Integration

The application includes a `PlainLanguageTranslator` in `privacy_protocol/privacy_protocol/plain_language_translator.py`.
**Functionality:**
- This component now primarily acts as a wrapper around the `gemini_api_client.py`.
- It attempts to call the Gemini Pro API to generate plain-language summaries for input clauses, using the AI category of the clause to provide context to the generative model via a structured prompt.
- If the Gemini API key is not configured, or if an API call fails (due to network issues, rate limits, content safety blocks, etc.), the translator falls back to providing predefined, category-based dummy explanations.

**Limitations of the Fallback Dummy Explanations:**
- **Generic Summaries:** The fallback summaries are category-based, not tailored to the specific content of the individual clause.
- **Not Data-Driven:** Fallback explanations are hardcoded.

### Roadmap to a Custom Trained AI Translation/Summarization Model (Alternative Strategy)

Replacing or supplementing the Gemini API with a custom-trained AI model (typically a sequence-to-sequence model) would involve:

1.  **Data Collection and Preparation (Parallel Corpus):** (Details as previously listed)
2.  **Model Selection (Sequence-to-Sequence Models):** (Details as previously listed)
3.  **Model Training/Fine-tuning:** (Details as previously listed)
4.  **Model Evaluation:** (Details as previously listed)
5.  **Model Serialization and Integration:** (Details as previously listed, would involve updating `PlainLanguageTranslator` to use the custom model)
6.  **Iteration and Refinement:** (Details as previously listed)

Developing a high-quality custom AI plain-language translator is a significant undertaking, with data collection for a parallel corpus being a primary challenge. The current Gemini API integration provides a powerful starting point.
