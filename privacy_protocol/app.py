import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Flask, render_template, request, redirect, url_for, flash
from privacy_protocol.interpreter import PrivacyInterpreter
from privacy_protocol.user_preferences import load_user_preferences, save_user_preferences, PREFERENCE_KEYS
from privacy_protocol.recommendations_engine import RecommendationEngine
from privacy_protocol.llm_services import ACTIVE_LLM_PROVIDER_ENV_VAR, DEFAULT_LLM_PROVIDER, PROVIDER_GEMINI, PROVIDER_OPENAI # Import LLM config vars
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for flash messages

# --- App Startup Logging ---
active_provider_name = os.environ.get(ACTIVE_LLM_PROVIDER_ENV_VAR, DEFAULT_LLM_PROVIDER).lower()
print("--- Privacy Protocol App ---")
print(f"[CONFIG] Active LLM Provider target: {active_provider_name.upper()}")
print("  (Actual LLM service used by PlainLanguageTranslator is determined by its internal factory call)")
print(f"  To change, set {ACTIVE_LLM_PROVIDER_ENV_VAR}={PROVIDER_GEMINI} or {ACTIVE_LLM_PROVIDER_ENV_VAR}={PROVIDER_OPENAI}")
print(f"  Ensure the corresponding API key (GEMINI_API_KEY or OPENAI_API_KEY) is also set in your environment or .env file.")
print("---")


# Initialize interpreter and load keywords
interpreter = PrivacyInterpreter()
keywords_path = os.path.join(os.path.dirname(__file__), 'data', 'keywords.json')
if os.path.exists(keywords_path):
    interpreter.load_keywords_from_path(keywords_path)
    print(f"INFO: Keywords loaded from {keywords_path}")
else:
    print(f"WARNING: Keywords file not found at {keywords_path}. Keyword analysis will be limited.")

if interpreter.nlp is None:
    print("WARNING: spaCy model not loaded. AI Category and clause analysis will be limited.")

app.interpreter = interpreter # Attach for tests or other potential uses
recommendation_engine = RecommendationEngine() # Initialize RecommendationEngine

# Descriptions for preferences page
PREFERENCE_DESCRIPTIONS = {
    "data_selling_allowed": {
        "label": "Data Selling",
        "description": "Allow the service to sell your personal information to third parties."
    },
    "data_sharing_for_ads_allowed": {
        "label": "Data Sharing for Ads",
        "description": "Allow sharing your data with third parties for advertising purposes."
    },
    "data_sharing_for_analytics_allowed": {
        "label": "Data Sharing for Analytics",
        "description": "Allow sharing your data (often anonymized) for service analytics and improvement."
    },
    "cookies_for_tracking_allowed": {
        "label": "Cookies for Tracking",
        "description": "Allow the use of cookies and similar technologies for tracking your activity across sites/apps."
    },
    "policy_changes_notification_required": {
        "label": "Policy Change Alerts",
        "description": "Prioritize alerts if the policy indicates how changes are communicated or if changes are frequent."
    },
    "childrens_privacy_strict": {
        "label": "Children's Privacy Protection",
        "description": "Apply stricter scrutiny or alerts for clauses related to children's data."
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    policy_text = request.form.get('policy_text', '')
    # Load current user preferences for this analysis
    user_prefs = load_user_preferences()
    # Pass preferences to interpreter instance attached to app
    app.interpreter.load_user_preferences(user_prefs)

    analysis_results = app.interpreter.analyze_text(policy_text)
    risk_assessment = app.interpreter.calculate_risk_assessment(analysis_results)
    # Augment analysis_results with recommendations (modifies analysis_results in-place)
    recommendation_engine.augment_analysis_with_recommendations(analysis_results)

    return render_template('results.html',
                            policy_text=policy_text,
                            analysis_results=analysis_results,
                            risk_assessment=risk_assessment,
                            nlp_available=(app.interpreter.nlp is not None))

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST':
        current_prefs = load_user_preferences() # Load existing to update
        for key in PREFERENCE_KEYS.keys(): # Iterate through defined keys
            # HTML form sends 'true'/'false' as strings
            submitted_value = request.form.get(key)
            if submitted_value == 'true':
                current_prefs[key] = True
            elif submitted_value == 'false':
                current_prefs[key] = False
            # else: maintain existing value if key not in form (should not happen with select)

        if save_user_preferences(current_prefs):
            flash('Preferences saved successfully!', 'success')
        else:
            flash('Failed to save preferences.', 'error')
        return redirect(url_for('preferences')) # Redirect to refresh and show flash message

    # For GET request
    user_prefs = load_user_preferences()
    return render_template('preferences.html', preferences=user_prefs, preference_descriptions=PREFERENCE_DESCRIPTIONS)

if __name__ == '__main__':
    # Ensure user_data directory and default files are set up on first run if not already
    # This is particularly for direct `python app.py` execution.
    # In a typical Flask deployment (e.g. with Gunicorn), this might be handled by an init script or startup hook.
    user_data_dir_path = os.path.join(os.path.dirname(__file__), 'user_data')
    default_prefs_file_path = os.path.join(user_data_dir_path, 'default_preferences.json')

    if not os.path.exists(default_prefs_file_path):
        print("INFO: default_preferences.json not found. Initializing user preferences storage...")
        # This call will create user_data dir and current_user_preferences.json from defaults
        # (which in turn tries to load default_preferences.json, potentially from hardcoded if file is also missing)
        load_user_preferences()
        print("INFO: Initialization check complete.")
    else:
        # If default_preferences.json exists, ensure current_user_preferences.json is also primed if missing
        load_user_preferences()


    app.run(debug=True, host='0.0.0.0', port=5000)
