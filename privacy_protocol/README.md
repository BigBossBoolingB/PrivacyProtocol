# Privacy Protocol

Privacy Protocol is an application designed to analyze privacy policy text. It identifies key clauses, categorizes them using a (currently rule-based, planned for ML) AI classifier, generates plain-language summaries (using Google's Gemini Pro API), and assesses potential privacy risks based on user preferences. Users can interact with the analyzer via a web interface.

## Features (Current & Planned)

-   **Policy Text Analysis:** Accepts pasted privacy policy text.
-   **Sentence Segmentation:** Uses spaCy to break down the policy into individual sentences/clauses.
-   **AI-Powered Clause Categorization:** Each clause is assigned a category (e.g., Data Collection, Data Sharing). (Currently rule-based, see `ML_MODEL_README.md`).
-   **Keyword Spotting:** Identifies specific keywords within clauses and provides explanations.
-   **Plain Language Summaries:** Generates easy-to-understand summaries for clauses using the Gemini Pro API (requires API key). Falls back to predefined explanations if API is unavailable.
-   **User Preference Management:** Allows users to set their privacy preferences (e.g., allowance for data selling, ad tracking).
-   **Personalized Risk Assessment:** Calculates a risk score and highlights clauses of high, medium, or low concern based on user preferences.
-   **Actionable Recommendations:** Provides suggestions based on the analysis and user concern levels.
-   **Web Interface:** User-friendly interface for pasting text, viewing analysis, and managing preferences.

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

5.  **Set up Gemini API Key (for Plain Language Summaries):**
    -   This application uses the Google Gemini Pro API to generate plain language summaries of policy clauses.
    -   Obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey) (or Google Cloud Vertex AI).
    -   Set the API key as an environment variable named `GEMINI_API_KEY`. You can do this in your shell:
        ```bash
        export GEMINI_API_KEY="your_actual_api_key_here"
        ```
        (On Windows, use `set GEMINI_API_KEY="your_actual_api_key_here"`)
    -   Alternatively, you can create a file named `.env` in the project root directory (`privacy_protocol/`) by copying from `.env.example`:
        ```bash
        cp .env.example .env
        ```
        Then, edit the `.env` file and replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual key. The application will attempt to load this if `python-dotenv` is integrated (though current `gemini_api_client.py` relies on the environment variable being directly set or loaded externally).
    -   **Important:** If you create a `.env` file, ensure it is listed in `.gitignore` (it is by default in this project's `.gitignore`) to prevent accidentally committing your API key.
    -   If the API key is not configured, the plain language summary feature will fall back to predefined dummy explanations.

## Running the Application

1.  **Ensure your virtual environment is activated.**
2.  **Set the `FLASK_APP` environment variable:**
    ```bash
    export FLASK_APP=app.py
    # On Windows: set FLASK_APP=app.py
    ```
    (Note: `app.py` is inside the `privacy_protocol` directory, so ensure your `PYTHONPATH` is set correctly if running from outside, or `cd privacy_protocol` first if `FLASK_APP` is set to just `app.py` relative to the `privacy_protocol` directory itself. The provided instructions assume you are in the outer `privacy_protocol` directory that contains the `app.py` file directly at that level).
    If your current directory is the root of the project (`privacy_protocol/`), and `app.py` is also at this level, then `export FLASK_APP=app.py` is correct.

3.  **Run the Flask development server:**
    ```bash
    flask run --host=0.0.0.0 --port=5000
    ```
    Or, for development, you can also run `python app.py` directly if `app.run(debug=True)` is enabled in `app.py`.

4.  Open your web browser and navigate to `http://0.0.0.0:5000/`.

## Running Tests

To run all unit tests:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
This command should be run from the project root directory (`privacy_protocol/`).

## Project Structure
(A brief overview of the main directories and files can be added here if desired, e.g., `app.py`, `privacy_protocol/` package, `templates/`, `tests/`, `user_data/`).

## Further Development
See `ML_MODEL_README.md` for details on the roadmap for the AI components (clause classification and plain language translation).
See `FUTURE_DEVELOPMENT.md` for a broader list of potential enhancements.
