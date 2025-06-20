import os
from flask import Flask, render_template, request, redirect, url_for, flash
# Removed duplicate Flask import
from privacy_protocol.interpreter import PrivacyInterpreter
from privacy_protocol.user_preferences import load_user_preferences, save_user_preferences, PREFERENCE_KEYS
from privacy_protocol.recommendations_engine import RecommendationEngine
from privacy_protocol.llm_services import ACTIVE_LLM_PROVIDER_ENV_VAR, DEFAULT_LLM_PROVIDER, PROVIDER_GEMINI, PROVIDER_OPENAI, PROVIDER_ANTHROPIC, PROVIDER_AZURE_OPENAI
from privacy_protocol.policy_history_manager import (
    save_policy_analysis,
    generate_policy_identifier,
    get_latest_policy_analysis, # Added
    list_analyzed_policies, # Ensured present for history_list route
    get_policy_analysis,     # Ensured present for view_historical_analysis route
    get_all_service_profiles_for_dashboard, # Added for dashboard
    load_user_privacy_profile # Added for dashboard user profile
)
import os # Removed duplicate os import
import difflib # Added

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

    diff_html = None
    latest_saved_analysis = get_latest_policy_analysis()

    if latest_saved_analysis:
        previous_analysis_text = latest_saved_analysis.get('full_policy_text')
        if previous_analysis_text and policy_text.strip() != previous_analysis_text.strip():
            prev_lines = previous_analysis_text.splitlines(keepends=True)
            current_lines = policy_text.splitlines(keepends=True)
            html_diff_maker = difflib.HtmlDiff(tabsize=4, wrapcolumn=70)
            diff_html = html_diff_maker.make_table(
                prev_lines, current_lines,
                fromdesc='Previous Version (from History)',
                todesc='Current Text Submitted'
            )
        elif previous_analysis_text and policy_text.strip() == previous_analysis_text.strip():
            diff_html = "<p>No textual changes detected compared to the most recent analysis in history.</p>"
    else:
        diff_html = "<p>No previous analysis found in history to compare against.</p>"

    # Save the current analysis to history (after diffing)
    if policy_text.strip():
        policy_id = generate_policy_identifier()
        source_description = "Pasted Text Input"
        save_policy_analysis(
            identifier=policy_id,
            policy_text=policy_text,
            analysis_results=analysis_results,
            risk_assessment=risk_assessment,
            source_url=source_description
        )

    return render_template('results.html',
                            policy_text=policy_text,
                            analysis_results=analysis_results,
                            risk_assessment=risk_assessment,
                            diff_html=diff_html, # Pass the diff HTML
                            nlp_available=(app.interpreter.nlp is not None),
                            page_title="Live Analysis Results") # Keep existing dynamic title logic if any

# Route for listing historical analyses
@app.route('/history', endpoint='history_list_route_function') # Ensure endpoint name matches url_for calls
def history_list_route_function():
    service_profiles = get_all_service_profiles_for_dashboard() # This loads and sorts ServiceProfiles
    return render_template(
        'history.html',
        service_profiles=service_profiles,
        page_title="Policy Analysis History"
    )

@app.route('/history/view/<policy_identifier>')
def view_historical_analysis(policy_identifier):
    stored_analysis_data = get_policy_analysis(policy_identifier) # Ensure this is imported
    if stored_analysis_data:
        current_nlp_available_status = app.interpreter.nlp is not None

        return render_template(
            'results.html',
            policy_text=stored_analysis_data.get('full_policy_text', ''),
            analysis_results=stored_analysis_data.get('analysis_results', []),
            risk_assessment=stored_analysis_data.get('risk_assessment', {}),
            is_historical_view=True,
            page_title=f"Stored Analysis: {stored_analysis_data.get('policy_identifier', 'N/A')} ({stored_analysis_data.get('analysis_timestamp', 'N/A')[:19].replace('T', ' ')})",
            diff_html=None,
            nlp_available=current_nlp_available_status,
            # For the banner in results.html, if using the alternative approach
            analysis_timestamp=stored_analysis_data.get('analysis_timestamp'),
            source_url=stored_analysis_data.get('source_url')
        )
    else:
        flash(f'Could not find stored analysis with ID: {policy_identifier}', 'error')
        return redirect(url_for('history_list'))

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

@app.route('/dashboard')
def dashboard_overview():
    service_profiles = get_all_service_profiles_for_dashboard()
    user_profile_data = load_user_privacy_profile() # New: load the aggregated profile

    # key_privacy_insights will come from user_profile_data.key_privacy_insights
    # If user_profile_data is None, the template should handle it.

    return render_template(
        'privacy_dashboard.html',
        service_profiles=service_profiles,
        user_profile=user_profile_data, # Pass the whole profile object
        page_title="Your Privacy Dashboard" # Updated title
    )

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
