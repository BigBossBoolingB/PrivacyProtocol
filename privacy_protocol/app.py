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
    get_latest_policy_analysis,
    list_analyzed_policies,
    get_policy_analysis,
    get_all_service_profiles_for_dashboard,
    load_user_privacy_profile,
    set_user_defined_name, # Added for renaming service
    calculate_and_save_user_privacy_profile # Added for updating profile after rename
)
from flask import jsonify # Added for API response
import os
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
        "description": "Controls whether policy clauses related to the selling of your personal data are flagged with high concern. Set to 'Not Allowed' to activate these high concern alerts."
    },
    "data_sharing_for_ads_allowed": {
        "label": "Data Sharing for Targeted Ads",
        "description": "Controls if sharing data with third parties specifically for targeted advertising purposes is flagged with high concern. Set to 'Not Allowed' for high concern alerts on such clauses."
    },
    "data_sharing_for_analytics_allowed": {
        "label": "Data Sharing for Analytics",
        "description": "Allow sharing your data (often anonymized) for service analytics and improvement. Setting to 'Not Allowed' may raise concern for clauses about analytics if they seem overly broad or non-essential."
    },
    "cookies_for_tracking_allowed": {
        "label": "Cookies for Cross-Site Tracking",
        "description": "Controls if the use of cookies and similar technologies for tracking your activity across different websites or apps is flagged with high concern. Set to 'Not Allowed' for high concern alerts."
    },
    "policy_changes_notification_required": {
        "label": "Highlight Policy Change Clauses",
        "description": "Set to 'Allowed' to have clauses describing how policy changes are communicated highlighted for your review (typically as Medium concern)."
    },
    "childrens_privacy_strict": {
        "label": "Strict Scrutiny for Children's Privacy",
        "description": "Set to 'Allowed' to apply stricter scrutiny to clauses related to children's data, flagging them with High concern."
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

@app.route('/api/service/<service_id>/set_name', methods=['POST'])
def api_set_service_name(service_id):
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Invalid request: Content-Type must be application/json'}), 400

    data = request.get_json()
    new_user_defined_name = data.get('user_defined_name')

    if new_user_defined_name is None: # Key must be present, value can be empty string to clear
        return jsonify({'success': False, 'message': 'Missing new_user_defined_name in request body'}), 400

    if len(new_user_defined_name.strip()) > 100: # Example length limit
       return jsonify({'success': False, 'message': 'New name is too long (max 100 characters).'}), 400

    success = set_user_defined_name(service_id, new_user_defined_name)

    if success:
        # After successfully renaming, also update the overall user privacy profile
        calculate_and_save_user_privacy_profile() # Uses default_user
        return jsonify({'success': True, 'message': 'Service name updated successfully.'})
    else:
        # Distinguish between service not found and other potential save errors if possible
        # For now, assuming set_user_defined_name returns False mainly for "not found"
        return jsonify({'success': False, 'message': 'Service not found or failed to update name.'}), 404

@app.route('/dashboard')
def dashboard_overview():
    service_profiles = get_all_service_profiles_for_dashboard()
    user_profile_data = load_user_privacy_profile() # New: load the aggregated profile

    # key_privacy_insights will come from user_profile_data.key_privacy_insights
    # If user_profile_data is None, the template should handle it.

    global_recommendations = []
    if user_profile_data: # Ensure user_profile_data is not None
        global_recommendations = recommendation_engine.generate_global_recommendations(user_profile_data)
    # else: global_recommendations remains [] which template handles

    return render_template(
        'privacy_dashboard.html',
        service_profiles=service_profiles,
        user_profile=user_profile_data, # Pass the whole profile object
        global_recommendations=global_recommendations, # Pass global recommendations
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
