# Privacy Protocol

Privacy Protocol is an application designed to analyze privacy policy text. It identifies key clauses, categorizes them using a (currently rule-based, planned for ML) AI classifier, generates plain-language summaries using a configurable LLM provider (Google Gemini, OpenAI GPT, Anthropic Claude, or Azure OpenAI), and assesses potential privacy risks based on user preferences. Users can interact with the analyzer via a web interface.

## Features (Current & Planned)

-   **Policy Text Analysis:** Accepts pasted privacy policy text.
-   **Sentence Segmentation:** Uses spaCy to break down the policy into individual sentences/clauses.
-   **AI-Powered Clause Categorization:** Each clause is assigned a category (e.g., Data Collection, Data Sharing). (Currently rule-based, see `ML_MODEL_README.md`).
-   **Keyword Spotting:** Identifies specific keywords within clauses and provides explanations.
-   **Configurable Plain Language Summaries:** Generates easy-to-understand summaries for clauses using a choice of LLM providers. Requires an API key for the chosen provider. Falls back to predefined explanations if the selected API is unavailable.
-   **User Preference Management:** Allows users to set their privacy preferences (e.g., allowance for data selling, ad tracking).
-   **Personalized Risk Assessment:** Calculates a risk score and highlights clauses of high, medium, or low concern based on user preferences.
-   **Actionable Recommendations:** Provides suggestions based on the analysis and user concern levels.
   - **Enhanced Risk Scoring:** For each analyzed policy, a `Service Risk Score` (0-100) is calculated and prominently displayed. This score is color-coded (Green for Low, Yellow for Medium, Red for High risk) and helps you quickly assess the potential privacy implications based on both AI-detected clause categories and your personalized concern settings. Counts of high, medium, and low concern clauses, along with the total number of clauses analyzed, provide further context.
-   **Web Interface:** User-friendly interface for pasting text, viewing analysis, and managing preferences.
     *   **Policy History & Change Tracking (`/history`):**
         *   **Automatic History:** Every policy text you analyze is automatically saved along with its detailed analysis results (AI categorization, keyword flags, plain language summaries, risk assessment, and recommendations).
         *   **View Past Analyses:** Navigate to the `/history` page to see a list of all your saved analyses, sorted by date. From there, you can click to view the full results of any specific past analysis.
         *   **Basic Change Detection:** When analyzing new text, it's compared against the most recent version in history. Differences are highlighted on the results page.
         *   **Storage:** Policy history is stored locally in JSON files within the `privacy_protocol/policy_history/` directory.
     *   **Privacy Dashboard (`/dashboard`):** The dashboard provides a consolidated overview of your privacy posture based on all policies you've analyzed:
         *   **Overall User Privacy Risk Score:** A prominent score (0-100, color-coded Green/Yellow/Red) gives you an at-a-glance understanding of your aggregated privacy risk across all tracked services. This is currently calculated as an average of the individual service risk scores.
         *   **Key Privacy Insights:** The dashboard synthesizes basic insights from your analyzed policies, such as highlighting if services have high-risk scores. (Note: Insight generation is currently basic and will be enhanced in the future).
         *   **Aggregated Statistics:** View totals for services analyzed, and counts of services falling into High, Medium, and Low risk categories based on their individual scores.
         *   **Per-Service Breakdown:** See a list of each individual policy analysis session, its specific `Service Risk Score` (0-100, color-coded), the date of analysis, and a link to its detailed results page.
         *   **Always Up-to-Date:** The dashboard data, including the overall score and service list, is automatically updated each time you analyze a new policy or re-analyze an existing one.

## Prerequisites

-   Python 3.9+
-   pip (Python package installer)
-   spaCy English model (`en_core_web_sm`)

## Setup & Configuration

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd privacy_protocol
    ```
    *(Note: The project root directory is named `privacy_protocol`. The main Python package is also named `privacy_protocol` inside this root.)*

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download spaCy Model:**
    ```bash
    python -m spacy download en_core_web_sm
    ```

5.  **Set up API Keys for LLM Providers (for Plain Language Summaries):**
    This application can use different Large Language Models for generating plain language summaries. You need to provide an API key for the service you intend to use. Refer to `.env.example` for a template. For development, you can create a `.env` file in the project root directory (`privacy_protocol/`) or set environment variables directly in your shell.

    -   **Gemini (Google):** Set the `GEMINI_API_KEY` environment variable.
        ```bash
        export GEMINI_API_KEY="your_gemini_api_key_here"
        ```
    -   **OpenAI (GPT models):** Set the `OPENAI_API_KEY` environment variable.
        ```bash
        export OPENAI_API_KEY="your_openai_api_key_here"
        ```
    -   **Anthropic (Claude models):** Set the `ANTHROPIC_API_KEY` environment variable.
        ```bash
        export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
        ```
    -   **Microsoft Azure OpenAI Service:** Set the following environment variables:
        ```bash
        export AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
        export AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint_url"
        export AZURE_OPENAI_DEPLOYMENT_NAME="your_azure_deployment_name"
        export AZURE_OPENAI_API_VERSION="your_api_version_e.g_2023-07-01-preview"
        ```
    **Important:** If you create a `.env` file, ensure it is listed in `.gitignore` (it is by default) to prevent accidentally committing your API keys. If an API key for the selected provider is not configured, the plain language summary feature will fall back to predefined dummy explanations.

6.  **Selecting the Active LLM Provider:**
    Set the `ACTIVE_LLM_PROVIDER` environment variable to choose which LLM service to use for summaries. Supported values are:
    -   `gemini` (Default)
    -   `openai`
    -   `anthropic`
    -   `azure_openai`

    Example:
    ```bash
    export ACTIVE_LLM_PROVIDER="azure_openai"
    ```
    If not set, the application defaults to Gemini. The application will indicate the active LLM provider target on startup.

## Running the Application

1.  **Ensure your virtual environment is activated and you are in the project root directory (`privacy_protocol/`).**
2.  **Set the `FLASK_APP` environment variable (if not using `python app.py` directly):**
    ```bash
    export FLASK_APP=app.py
    # On Windows: set FLASK_APP=app.py
    ```
3.  **Run the Flask development server:**
    ```bash
    flask run --host=0.0.0.0 --port=5000
    ```
    Alternatively, for development, you can run `python app.py` directly from the project root directory, as `app.py` includes `app.run(debug=True)`.

4.  Open your web browser and navigate to `http://0.0.0.0:5000/`.
5.  Access the `/history` page to review previously analyzed policies.
6.  Visit the `/dashboard` page for an overview of your analyzed services and their risk scores.

## Running Tests

To run all unit tests:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
This command should be run from the project root directory (`privacy_protocol/`). Note: The `tests` directory is directly under the project root.

## Project Structure
- `app.py`: Main Flask application file.
- `privacy_protocol/`: The core Python package.
  - `__init__.py`: Marks the directory as a package and exports key components.
  - `interpreter.py`: Core analysis logic.
  - `ml_classifier.py`: Dummy AI clause classifier.
  - `plain_language_translator.py`: Handles plain language summaries, using LLM services.
  - `recommendations_engine.py`: Generates actionable recommendations.
  - `user_preferences.py`: Manages user privacy settings.
  - `llm_services/`: Sub-package for different LLM API clients.
    - `base_llm_service.py`: Abstract base class for LLM services.
    - `gemini_api_client.py`: Gemini client.
    - `openai_api_client.py`: OpenAI client.
    - `anthropic_api_client.py`: Anthropic client.
    - `azure_openai_client.py`: Azure OpenAI client. # Added
    - `llm_service_factory.py`: Factory to select and instantiate an LLM service.
  - `clause_categories.py`, `recommendations_data.py`: Data modules.
- `templates/`: HTML templates for the web interface.
- `tests/`: Unit tests for the application. All test files are located here directly.
- `user_data/`: Stores user preferences (e.g., `current_user_preferences.json`).
- `policy_history/`: Stores saved policy analyses as JSON files.
- `requirements.txt`: Python dependencies.
- `README.md`: This file.
- `ML_MODEL_README.md`: Details on AI model development.
- `FUTURE_DEVELOPMENT.md`: Ideas for future enhancements.
- `.env.example`: Example for API key configuration.
- `.gitignore`: Specifies intentionally untracked files.

## Further Development
See `ML_MODEL_README.md` for details on the roadmap for the AI components.
See `FUTURE_DEVELOPMENT.md` for a broader list of potential enhancements.
