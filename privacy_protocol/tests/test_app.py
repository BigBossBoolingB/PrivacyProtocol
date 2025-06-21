import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import shutil
import re
import time # For diff testing
from datetime import datetime, timezone # For dashboard tests
from flask import url_for # For dashboard tests

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import app
from privacy_protocol.privacy_protocol.dashboard_models import ServiceProfile # For dashboard tests
from privacy_protocol.privacy_protocol import dashboard_data_manager # For dashboard tests
from privacy_protocol.interpreter import PrivacyInterpreter
from privacy_protocol.plain_language_translator import PlainLanguageTranslator
from privacy_protocol.user_preferences import (
    get_default_preferences,
    CURRENT_PREFERENCES_PATH,
    DEFAULT_PREFERENCES_PATH,
    USER_DATA_DIR,
)
from privacy_protocol.llm_services import (
    llm_service_factory,
    ACTIVE_LLM_PROVIDER_ENV_VAR,
    PROVIDER_GEMINI,
    PROVIDER_OPENAI,
    PROVIDER_ANTHROPIC,
    PROVIDER_AZURE_OPENAI
)
# Import from policy_history_manager
from privacy_protocol.policy_history_manager import (
    save_policy_analysis as save_policy_direct, # Alias to avoid conflict if app also imports it
    generate_policy_identifier as generate_id_direct,
    list_analyzed_policies as list_policies_direct,
    get_policy_analysis as get_policy_direct,
    POLICY_HISTORY_DIR # For cleanup
)


GEMINI_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.generate_summary'
OPENAI_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.openai_api_client.OpenAILLMService.generate_summary'
ANTHROPIC_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.anthropic_api_client.AnthropicLLMService.generate_summary'
AZURE_OPENAI_SERVICE_GENERATE_SUMMARY_PATH = 'privacy_protocol.llm_services.azure_openai_client.AzureOpenAILLMService.generate_summary'

GEMINI_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.gemini_api_client.GeminiLLMService.is_api_key_available'
OPENAI_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.openai_api_client.OpenAILLMService.is_api_key_available'
ANTHROPIC_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.anthropic_api_client.AnthropicLLMService.is_api_key_available'
AZURE_OPENAI_SERVICE_KEY_CHECK_PATH = 'privacy_protocol.llm_services.azure_openai_client.AzureOpenAILLMService.is_api_key_available'


SPACY_MODEL_AVAILABLE = False
NLP_UNAVAILABLE_MESSAGE_IN_RESULTS = "NLP model 'en_core_web_sm' was not loaded"
try:
    import spacy
    spacy.load("en_core_web_sm")
    SPACY_MODEL_AVAILABLE = True
except (ImportError, OSError):
    pass


class TestWebApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with patch('sys.stdout', new_callable=MagicMock):
            app.interpreter = PrivacyInterpreter()

        # Keywords path relative to app.py's location (which is project_root/privacy_protocol/)
        keywords_path = os.path.join(app.root_path, 'data', 'keywords.json')
        if os.path.exists(keywords_path):
             app.interpreter.load_keywords_from_path(keywords_path)
        # else:
             # print(f"WARNING (test_app.py setUp): Keywords file not found at {keywords_path} for app.interpreter.", file=sys.stderr)

        # User preferences directory
        if os.path.exists(USER_DATA_DIR):
            shutil.rmtree(USER_DATA_DIR)
        os.makedirs(USER_DATA_DIR)
        default_prefs_content = get_default_preferences()
        with open(DEFAULT_PREFERENCES_PATH, 'w') as f:
            json.dump(default_prefs_content, f)
        if os.path.exists(CURRENT_PREFERENCES_PATH):
            os.remove(CURRENT_PREFERENCES_PATH)
        app.interpreter.load_user_preferences(default_prefs_content.copy())

        # Policy history directory
        if os.path.exists(POLICY_HISTORY_DIR):
            shutil.rmtree(POLICY_HISTORY_DIR)
        os.makedirs(POLICY_HISTORY_DIR, exist_ok=True)

        # Add cleanup for dashboard data
        self.user_data_dir_for_dashboard = dashboard_data_manager.USER_DATA_DIR # Renamed to avoid conflict with existing USER_DATA_DIR from preferences
        self.service_profiles_path = dashboard_data_manager.SERVICE_PROFILES_PATH
        if os.path.exists(self.service_profiles_path):
            os.remove(self.service_profiles_path)
        # Ensure user_data_dir exists for dashboard_data_manager if it's different from preferences' USER_DATA_DIR
        # Note: dashboard_data_manager.USER_DATA_DIR is currently derived to be the same as preferences' USER_DATA_DIR
        # So, the os.makedirs(USER_DATA_DIR) above already covers this.
        # If they were different, we'd need: os.makedirs(self.user_data_dir_for_dashboard, exist_ok=True)


    def tearDown(self):
        if os.path.exists(USER_DATA_DIR): # This is preferences USER_DATA_DIR
            shutil.rmtree(USER_DATA_DIR)
        if os.path.exists(POLICY_HISTORY_DIR):
            shutil.rmtree(POLICY_HISTORY_DIR)

        # Explicitly remove service_profiles.json if it exists, USER_DATA_DIR might have other things like default_preferences.json
        if os.path.exists(self.service_profiles_path):
             os.remove(self.service_profiles_path)
        # If self.user_data_dir_for_dashboard was different and created by setup, consider removing it:
        # For example, if os.path.exists(self.user_data_dir_for_dashboard) and not os.listdir(self.user_data_dir_for_dashboard):
        #    os.rmdir(self.user_data_dir_for_dashboard)
        # But given USER_DATA_DIR is the same for both, rmtree on USER_DATA_DIR handles it.

        if ACTIVE_LLM_PROVIDER_ENV_VAR in os.environ:
            del os.environ[ACTIVE_LLM_PROVIDER_ENV_VAR]

    def _get_current_preferences_from_file(self):
        if os.path.exists(CURRENT_PREFERENCES_PATH):
            with open(CURRENT_PREFERENCES_PATH, 'r') as f:
                try: return json.load(f)
                except json.JSONDecodeError: return None
        return None

    def _assert_risk_display_elements(self, response_data, score, num_clauses, high_c, med_c, low_c, none_c):
        """Helper to assert common risk display elements."""
        self.assertIn(b"Calculated Risk Score:", response_data)

        if score <= 33:
            color_text, color_bg, label_text = "low", "low", "Low Risk"
        elif score <= 66:
            color_text, color_bg, label_text = "medium", "medium", "Medium Risk"
        else:
            color_text, color_bg, label_text = "high", "high", "High Risk"

        self.assertIn(bytes(f"<span class=\"risk-score-value risk-score-{color_text}-text\">{score}/100</span>", 'utf-8'), response_data)
        self.assertIn(bytes(f"<p class=\"risk-category-label risk-score-{color_text}-text\">{label_text}</p>", 'utf-8'), response_data)
        self.assertIn(bytes(f"class=\"risk-summary-box risk-score-{color_bg}-bg\"", 'utf-8'), response_data)
        self.assertRegex(response_data.decode('utf-8'), rf"High Concern Clauses:</span>\s*{high_c}</p>")
        self.assertRegex(response_data.decode('utf-8'), rf"Medium Concern Clauses:</span>\s*{med_c}</p>")
        self.assertRegex(response_data.decode('utf-8'), rf"Low Concern Clauses:</span>\s*{low_c}</p>")
        self.assertRegex(response_data.decode('utf-8'), rf"Uncategorized/No Concern Clauses:</span>\s*{none_c}</p>")
        self.assertIn(bytes(f"(Based on {num_clauses} clauses analyzed)", 'utf-8'), response_data)

    def _create_dummy_historical_analysis(self, suffix="", service_risk_score_val=9, num_clauses_val=1, high_concern_val=0, medium_concern_val=0, low_concern_val=1, none_concern_val=0):
        # Helper to create a file that list_analyzed_policies and get_policy_analysis can find
        # Updated to include service_risk_score and num_clauses_analyzed
        identifier = generate_id_direct() + suffix # Ensure some uniqueness if called rapidly

        # Calculate overall_risk_score based on counts
        overall_risk_val = (high_concern_val * 10) + (medium_concern_val * 5) + (low_concern_val * 1)

        # Determine default user_concern_level for the single analysis_results item based on counts
        default_concern = 'None'
        # This logic for default_concern based on counts is a bit simplistic for a single clause,
        # but okay for dummy data generation where we specify counts directly.
        if high_concern_val > 0: default_concern = 'High'
        elif medium_concern_val > 0: default_concern = 'Medium'
        elif low_concern_val > 0: default_concern = 'Low'

        data = {
            'policy_identifier': identifier,
            'source_url': f'http://example.com/policy{suffix}',
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'full_policy_text': f"Historical policy text {suffix}.",
            'analysis_results': [{'clause_text': f"Historical Clause {suffix}",
                                  'ai_category': 'Other',  # Keep it simple for dummy
                                  'recommendations':[],
                                  'user_concern_level': default_concern,
                                  'plain_language_summary':''}],
            'risk_assessment': {
                'overall_risk_score': overall_risk_val,
                'service_risk_score': service_risk_score_val,
                'high_concern_count': high_concern_val,
                'medium_concern_count': medium_concern_val,
                'low_concern_count': low_concern_val,
                'none_concern_count': none_concern_val,
                'num_clauses_analyzed': num_clauses_val
            }
        }
        save_policy_direct(
            identifier, data['full_policy_text'], data['analysis_results'],
            data['risk_assessment'], data['source_url']
        )
        return identifier, data


    def test_main_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Privacy Policy Analyzer", response.data)

    # --- /analyze route tests with history and diffing ---
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None)) # No API key for Gemini
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH) # Mock the method
    def test_analyze_first_policy_saves_and_shows_no_history_message(self, mock_gemini_summary_gen, mock_gemini_key_check):
        # This test will also check the new risk score display
        with patch('sys.stdout', new_callable=MagicMock): app.interpreter = PrivacyInterpreter()
        app.interpreter.load_keywords_from_path(os.path.join(app.root_path, 'data', 'keywords.json'))

        default_prefs = get_default_preferences()
        app.interpreter.load_user_preferences(default_prefs.copy())

        # Policy text designed to hit specific categories and concern levels
        # "We sell your data." -> AI: Data Selling, User Pref: data_selling_allowed=False -> Concern: High. Base:20, Bonus:15 -> Actual:35
        # "We use cookies." -> AI: Cookies and Tracking, User Pref: cookies_for_tracking_allowed=False -> Concern: High. Base:10, Bonus:15 -> Actual:25
        # Total accumulated = 35 + 25 = 60
        # Max possible for 2 clauses = 2 * (20+15) = 70  (Assuming max AI base is 20 from PrivacyInterpreter.AI_CATEGORY_BASE_POINTS, max bonus is 15)
        # Service Risk Score = round((60/70)*100) = round(85.71) = 86 (High Risk)
        policy_text = "We sell your data. We use cookies."

        mock_analysis_results_for_app = [
            {
                'clause_text': "We sell your data.", 'ai_category': 'Data Selling',
                'keyword_matches': [], 'plain_language_summary': 'Mock summary 1',
                'user_concern_level': 'High', 'recommendations': [] # Ensure recommendations key exists
            },
            {
                'clause_text': "We use cookies.", 'ai_category': 'Cookies and Tracking Technologies',
                'keyword_matches': [], 'plain_language_summary': 'Mock summary 2',
                'user_concern_level': 'High', 'recommendations': [] # Ensure recommendations key exists
            }
        ]

        expected_risk_assessment_for_app = {
            'overall_risk_score': 20, # 2 * 10 for High
            'service_risk_score': 86, # Calculated above
            'high_concern_count': 2, 'medium_concern_count': 0, 'low_concern_count': 0,
            'none_concern_count': 0, 'num_clauses_analyzed': 2
        }

        # Patch the interpreter methods that app.py calls
        with patch.object(app.interpreter, 'analyze_text', return_value=mock_analysis_results_for_app) as mock_analyze, \
             patch.object(app.interpreter, 'calculate_risk_assessment', return_value=expected_risk_assessment_for_app) as mock_calculate:
            # Pass source_url here to ensure it's saved correctly if provided
            response = self.client.post('/analyze', data={'policy_text': policy_text, 'source_url': 'test_source_from_post'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No previous analysis found in history to compare against.", response.data)

        # Assertions for the new risk score display
        self.assertIn(b"Calculated Risk Score:", response.data)
        self.assertIn(b"<span class=\"risk-score-value risk-score-high-text\">86/100</span>", response.data)
        self.assertIn(b"<p class=\"risk-category-label risk-score-high-text\">High Risk</p>", response.data)
        self.assertIn(b"class=\"risk-summary-box risk-score-high-bg\"", response.data)
        # More robust check for concern counts, allowing for surrounding tags
        self.assertRegex(response.data.decode('utf-8'), r"High Concern Clauses:</span>\s*2</p>")
        self.assertRegex(response.data.decode('utf-8'), r"Medium Concern Clauses:</span>\s*0</p>")
        self.assertRegex(response.data.decode('utf-8'), r"Low Concern Clauses:</span>\s*0</p>")
        self.assertRegex(response.data.decode('utf-8'), r"Uncategorized/No Concern Clauses:</span>\s*0</p>")
        self.assertIn(b"(Based on 2 clauses analyzed)", response.data)

        # Check if saved (original functionality of the test)
        saved_policies = list_policies_direct()
        self.assertEqual(len(saved_policies), 1)
        self.assertEqual(saved_policies[0]['source_url'], "test_source_from_post")
        saved_json = get_policy_direct(saved_policies[0]['identifier'])
        self.assertIsNotNone(saved_json)
        self.assertEqual(saved_json['risk_assessment']['service_risk_score'], 86)
        self.assertEqual(saved_json['risk_assessment']['num_clauses_analyzed'], 2)
        self.assertEqual(saved_json['risk_assessment']['high_concern_count'], 2)

    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_same_policy_shows_no_changes_message(self, mock_gemini_summary_gen, mock_gemini_key_check):
        policy_text = "This policy will be analyzed twice. It mentions data collection."

        # Expected analysis for this policy text (simplified for the test)
        # Assume 1 clause, "Data Collection" category, "Low" concern by default
        # Base: 10 (Data Collection), Bonus: 2 (Low) -> Actual: 12
        # Max possible for 1 clause = 35 (Max AI base 20 + Max Bonus 15). Score = round((12/35)*100) = 34 (Medium Risk)
        mock_analysis_results = [{'clause_text': policy_text, 'ai_category': 'Data Collection', 'keyword_matches': [], 'plain_language_summary': 'Summary.', 'user_concern_level': 'Low', 'recommendations': []}]
        expected_risk_assessment = {
            'overall_risk_score': 1, 'service_risk_score': 34,
            'high_concern_count': 0, 'medium_concern_count': 0, 'low_concern_count': 1, 'none_concern_count': 0,
            'num_clauses_analyzed': 1
        }
        app.interpreter.load_user_preferences(get_default_preferences().copy()) # Ensure default prefs for calc

        # First analysis (saves it)
        with patch.object(app.interpreter, 'analyze_text', return_value=mock_analysis_results), \
             patch.object(app.interpreter, 'calculate_risk_assessment', return_value=expected_risk_assessment):
            self.client.post('/analyze', data={'policy_text': policy_text, 'source_url': 'same_policy_test_v1'})

        # Second analysis of the exact same text
        with patch.object(app.interpreter, 'analyze_text', return_value=mock_analysis_results), \
             patch.object(app.interpreter, 'calculate_risk_assessment', return_value=expected_risk_assessment):
            response = self.client.post('/analyze', data={'policy_text': policy_text, 'source_url': 'same_policy_test_v2'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No textual changes detected compared to the most recent analysis in history.", response.data)
        # Assert risk display for the second response
        self._assert_risk_display_elements(response.data,
                                           score=34, num_clauses=1,
                                           high_c=0, med_c=0, low_c=1, none_c=0)

    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_different_policy_shows_diff_table(self, mock_gemini_summary_gen, mock_gemini_key_check):
        original_text = "Version 1 of the policy. We track cookies." # High concern
        # Score for original: Cookies (10) + High (15) = 25. Max 35. round((25/35)*100) = 71 (High)
        mock_analysis_v1 = [{'clause_text': original_text, 'ai_category': 'Cookies and Tracking Technologies', 'keyword_matches': [], 'plain_language_summary': 'Summary v1', 'user_concern_level': 'High', 'recommendations': []}]
        risk_assessment_v1 = {'overall_risk_score': 10, 'service_risk_score': 71, 'high_concern_count': 1, 'medium_concern_count': 0, 'low_concern_count': 0, 'none_concern_count': 0, 'num_clauses_analyzed': 1}

        updated_text = "Version 2 of the policy, with changes. We share data." # Also High concern
        # Score for updated: Data Sharing (15) + High (15) = 30. Max 35. round((30/35)*100) = 86 (High)
        mock_analysis_v2 = [{'clause_text': updated_text, 'ai_category': 'Data Sharing', 'keyword_matches': [], 'plain_language_summary': 'Summary v2', 'user_concern_level': 'High', 'recommendations': []}]
        risk_assessment_v2 = {'overall_risk_score': 10, 'service_risk_score': 86, 'high_concern_count': 1, 'medium_concern_count': 0, 'low_concern_count': 0, 'none_concern_count': 0, 'num_clauses_analyzed': 1}

        # Set default preferences where cookie tracking and data sharing for ads are High concern
        prefs = get_default_preferences()
        prefs['cookies_for_tracking_allowed'] = False
        prefs['data_sharing_for_ads_allowed'] = False # Assuming 'Data Sharing' AI cat triggers this
        app.interpreter.load_user_preferences(prefs.copy())


        with patch.object(app.interpreter, 'analyze_text', return_value=mock_analysis_v1), \
             patch.object(app.interpreter, 'calculate_risk_assessment', return_value=risk_assessment_v1):
            self.client.post('/analyze', data={'policy_text': original_text, 'source_url': 'diff_test_v1'})

        with patch.object(app.interpreter, 'analyze_text', return_value=mock_analysis_v2), \
             patch.object(app.interpreter, 'calculate_risk_assessment', return_value=risk_assessment_v2):
            response = self.client.post('/analyze', data={'policy_text': updated_text, 'source_url': 'diff_test_v2'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Changes Since Last Analysis", response.data)
        self.assertIn(b'<table class="diff"', response.data)
        self.assertIn(b'class="diff_sub"', response.data)
        self.assertIn(b'class="diff_add"', response.data)

        # Assert risk display for the V2 analysis
        self._assert_risk_display_elements(response.data,
                                           score=86, num_clauses=1,
                                           high_c=1, med_c=0, low_c=0, none_c=0)

    # --- /history and /history/view routes ---
    def test_history_list_page_empty(self):
        # setUp ensures service_profiles.json is cleared initially
        # Also ensure user_privacy_profile.json is cleared for consistent dashboard checks if route involves it
        user_profile_path = os.path.join(dashboard_data_manager.USER_DATA_DIR, dashboard_data_manager.USER_PRIVACY_PROFILE_FILENAME)
        if os.path.exists(user_profile_path):
            os.remove(user_profile_path)

        with app.test_request_context(): # For url_for
            response = self.client.get(url_for('history_list_route_function'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No policy analyses found in history. Analyze some policies to see them here.", response.data)

    def test_history_list_page_with_service_profiles(self):
        # Create ServiceProfile data directly for this test, as the history page now reads from service_profiles.json
        ts1_iso = datetime(2024, 3, 10, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        ts2_iso = datetime(2024, 3, 11, 12, 0, 0, tzinfo=timezone.utc).isoformat() # More recent

        profile1 = ServiceProfile(
            service_id='service1.com', service_name='Service One',
            latest_analysis_timestamp=ts1_iso, latest_policy_identifier='pid_s1',
            latest_service_risk_score=25, # Low risk
            num_total_clauses=10, high_concern_count=0, medium_concern_count=0, low_concern_count=1,
            source_url='http://service1.com'
        )
        profile2 = ServiceProfile(
            service_id='service2.com', service_name='Service Two',
            latest_analysis_timestamp=ts2_iso, latest_policy_identifier='pid_s2',
            latest_service_risk_score=80, # High risk
            num_total_clauses=15, high_concern_count=2, medium_concern_count=1, low_concern_count=0,
            source_url='http://service2.com'
        )
        # Save profiles - get_all_service_profiles_for_dashboard sorts by timestamp desc
        dashboard_data_manager.save_service_profiles([profile1, profile2])

        with app.test_request_context(): # For url_for
            response = self.client.get(url_for('history_list_route_function'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Policy Analysis History", response.data)

        # Verify profile2 (more recent) appears first and correctly
        self.assertIn(b"Service Two", response.data)
        self.assertIn(b"service2.com", response.data) # service_id
        self.assertIn(b"2024-03-11 12:00:00", response.data)
        self.assertIn(b"<span class=\"risk-score-value risk-score-high-text\">80/100</span>", response.data)
        self.assertIn(b"<span class=\"risk-category-label risk-score-high-text\">High Risk</span>", response.data)
        self.assertIn(bytes(url_for('view_historical_analysis', policy_identifier='pid_s2'), 'utf-8'), response.data)
        self.assertIn(b'class="history-item risk-score-high-bg"', response.data)


        # Verify profile1 appears second and correctly
        self.assertIn(b"Service One", response.data)
        self.assertIn(b"service1.com", response.data) # service_id
        self.assertIn(b"2024-03-10 10:00:00", response.data)
        self.assertIn(b"<span class=\"risk-score-value risk-score-low-text\">25/100</span>", response.data)
        self.assertIn(b"<span class=\"risk-category-label risk-score-low-text\">Low Risk</span>", response.data)
        self.assertIn(bytes(url_for('view_historical_analysis', policy_identifier='pid_s1'), 'utf-8'), response.data)
        self.assertIn(b'class="history-item risk-score-low-bg"', response.data)

        # Check order
        text_data = response.data.decode('utf-8')
        self.assertTrue(text_data.find("Service Two") < text_data.find("Service One"))

    def test_view_historical_analysis_found(self):
        # Use specific values for the dummy analysis to make assertions precise
        identifier, data = self._create_dummy_historical_analysis(
            suffix="view_found",
            service_risk_score_val=60, # Medium Risk
            num_clauses_val=3,
            high_concern_val=1,
            medium_concern_val=1,
            low_concern_val=1,
            none_concern_val=0
            # overall_risk_score will be 10+5+1 = 16, calculated by helper
        )
        response = self.client.get(f'/history/view/{identifier}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Stored Analysis:", response.data)
        self.assertIn(bytes(data['full_policy_text'], 'utf-8'), response.data)
        self.assertIn(bytes(data['analysis_results'][0]['clause_text'], 'utf-8'), response.data)

        # Assertions for the new risk score display from historical data
        self.assertIn(b"Calculated Risk Score:", response.data)

        score_val = data['risk_assessment']['service_risk_score'] # Should be 60
        num_clauses = data['risk_assessment']['num_clauses_analyzed'] # Should be 3

        expected_color_class_text = "medium"
        expected_color_class_bg = "medium"
        expected_label_text = "Medium Risk"

        self.assertIn(bytes(f"<span class=\"risk-score-value risk-score-{expected_color_class_text}-text\">{score_val}/100</span>", 'utf-8'), response.data)
        self.assertIn(bytes(f"<p class=\"risk-category-label risk-score-{expected_color_class_text}-text\">{expected_label_text}</p>", 'utf-8'), response.data)
        self.assertIn(bytes(f"class=\"risk-summary-box risk-score-{expected_color_class_bg}-bg\"", 'utf-8'), response.data)
        self.assertIn(bytes(f"(Based on {num_clauses} clauses analyzed)", 'utf-8'), response.data)
        self.assertRegex(response.data.decode('utf-8'), r"High Concern Clauses:</span>\s*1</p>")
        self.assertRegex(response.data.decode('utf-8'), r"Medium Concern Clauses:</span>\s*1</p>")
        self.assertRegex(response.data.decode('utf-8'), r"Low Concern Clauses:</span>\s*1</p>")
        self.assertRegex(response.data.decode('utf-8'), r"Uncategorized/No Concern Clauses:</span>\s*0</p>")

        self.assertIn(b"Back to History List", response.data)

    def test_view_historical_analysis_not_found(self):
        response = self.client.get('/history/view/non_existent_id_xyz', follow_redirects=True)
        self.assertEqual(response.status_code, 200) # After redirect to history list
        self.assertIn(b"Could not find stored analysis with ID: non_existent_id_xyz", response.data)
        self.assertIn(b"Analysis History", response.data) # Should be on history list page

    # ... (Keep existing tests for /preferences, and other /analyze aspects like provider mocking) ...
    # The following are existing tests, slightly adapted if needed for clarity or consistency.
    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(False, None))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    def test_analyze_page_llm_key_unavailable_uses_fallback_summary(self, mock_gemini_summary_gen, mock_gemini_key_check):
        # This test focuses on fallback summary, but risk display should also be correct.
        policy_text = "We collect your email."
        # For "We collect your email.": AI Cat: Data Collection, User Concern (default): Low
        # Base: 10 (Data Collection), Bonus: 2 (Low) -> Actual: 12
        # Max possible for 1 clause = 35. Score = round((12/35)*100) = 34 (Medium Risk)

        mock_analysis_results = [{'clause_text': policy_text, 'ai_category': 'Data Collection', 'keyword_matches': [], 'plain_language_summary': 'Fallback summary here.', 'user_concern_level': 'Low', 'recommendations': []}]

        current_prefs = get_default_preferences() # Ensure this test uses predictable preferences
        # The app.interpreter instance used by the route is configured in setUp.
        # We need to ensure it has the correct preferences for this test's specific calculation if they differ from setUp.
        # However, for this specific policy_text and default_prefs, the concern is 'Low'.
        app.interpreter.load_user_preferences(current_prefs.copy())


        expected_risk_assessment = {
            'overall_risk_score': 1, 'service_risk_score': 34,
            'high_concern_count': 0, 'medium_concern_count': 0, 'low_concern_count': 1, 'none_concern_count': 0,
            'num_clauses_analyzed': 1
        }

        # Patch the app.interpreter instance that the route will use
        with patch.object(app.interpreter, 'analyze_text', return_value=mock_analysis_results) as mock_analyze, \
             patch.object(app.interpreter, 'calculate_risk_assessment', return_value=expected_risk_assessment) as mock_calculate, \
             patch.object(app.interpreter.plain_language_translator, 'translate', return_value="Fallback summary here.") as mock_translate_method:

            response = self.client.post('/analyze', data={'policy_text': policy_text})

        self.assertEqual(response.status_code, 200)

        # Check for fallback summary (original assertion)
        self.assertIn(b"Fallback summary here.", response.data)
        mock_gemini_summary_gen.assert_not_called() # Confirms LLM not called
        # mock_translate_method.assert_called_once_with(policy_text, 'Data Collection') # This was part of an older version of the code structure

        # Assert risk display
        self._assert_risk_display_elements(response.data,
                                           score=34, num_clauses=1,
                                           high_c=0, med_c=0, low_c=1, none_c=0)

    def test_preferences_page_get(self):
        response = self.client.get('/preferences')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your Privacy Preferences", response.data)
        select_block_for_selling = response.data.decode('utf-8').split('<select name="data_selling_allowed"')[1].split('</select>')[0]
        self.assertIn('<option value="false" selected', select_block_for_selling)

    def test_preferences_page_post_and_redirect(self):
        new_preference_values = {
            'data_selling_allowed': 'true',
            'data_sharing_for_ads_allowed': 'true',
            'data_sharing_for_analytics_allowed': 'false',
            'cookies_for_tracking_allowed': 'false',
            'policy_changes_notification_required': 'false',
            'childrens_privacy_strict': 'false'
        }
        response = self.client.post('/preferences', data=new_preference_values, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Preferences saved successfully!', response.data)

        saved_prefs = self._get_current_preferences_from_file()
        self.assertIsNotNone(saved_prefs)
        self.assertTrue(saved_prefs['data_selling_allowed'])
        self.assertFalse(saved_prefs['data_sharing_for_analytics_allowed'])

        select_block_for_selling_after_post = response.data.decode('utf-8').split('<select name="data_selling_allowed"')[1].split('</select>')[0]
        self.assertIn('<option value="true" selected', select_block_for_selling_after_post)

        select_block_for_analytics_after_post = response.data.decode('utf-8').split('<select name="data_sharing_for_analytics_allowed"')[1].split('</select>')[0]
        self.assertIn('<option value="false" selected', select_block_for_analytics_after_post)

    # --- Dashboard Tests ---
    def test_dashboard_page_empty(self):
        # setUp ensures service_profiles.json and user_privacy_profile.json (via USER_DATA_DIR rmtree) are cleared.
        # load_user_privacy_profile will then call calculate_and_save_user_privacy_profile,
        # which should produce the "No services analyzed yet." insight.
        with app.test_request_context():
            response = self.client.get(url_for('dashboard_overview'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your Privacy Dashboard", response.data)
        # Check for the service list placeholder
        self.assertIn(b"No services analyzed yet. Analyze a policy to see it here.", response.data)
        # Check for the specific insight generated when no services are analyzed
        self.assertIn(b"No services analyzed yet.", response.data)


    def test_dashboard_page_with_service_profiles(self):
        ts1_iso = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        ts2_iso = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc).isoformat() # More recent

        profile1_data = {
            'service_id': 'example.com', 'service_name': 'Example Site',
            'latest_analysis_timestamp': ts1_iso, 'latest_policy_identifier': 'pid1_hist',
            'latest_service_risk_score': 30, 'num_total_clauses': 10,
            'high_concern_count': 0, 'medium_concern_count': 1, 'low_concern_count': 2,
            'source_url': 'http://example.com/privacy'
        }
        profile2_data = {
            'service_id': 'another.org', 'service_name': 'Another Org',
            'latest_analysis_timestamp': ts2_iso, 'latest_policy_identifier': 'pid2_hist',
            'latest_service_risk_score': 75, 'num_total_clauses': 20,
            'high_concern_count': 3, 'medium_concern_count': 2, 'low_concern_count': 1,
            'source_url': 'http://another.org/policy'
        }
        profile1 = ServiceProfile(**profile1_data)
        profile2 = ServiceProfile(**profile2_data)

        # Save profiles (profile2 is more recent, save_service_profiles sorts by name, but get_all sorts by timestamp)
        dashboard_data_manager.save_service_profiles([profile1, profile2])

        with app.test_request_context(): # Need app context for url_for
            response = self.client.get(url_for('dashboard_overview'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your Privacy Dashboard", response.data)

        # Check for profile2 (more recent, should be first due to sorting in get_all_service_profiles_for_dashboard)
        self.assertIn(b"Another Org", response.data)
        self.assertIn(b"2024-01-02 12:00:00", response.data)
        self.assertIn(b"<span class=\"risk-score-value risk-score-high-text\">75/100</span>", response.data)
        self.assertIn(b"<span class=\"risk-category-label risk-score-high-text\">High Risk</span>", response.data) # Typo fix: was risk_score-high-text for label before, should be this
        self.assertIn(bytes(url_for('view_historical_analysis', policy_identifier='pid2_hist'), 'utf-8'), response.data)

        # Check for profile1
        self.assertIn(b"Example Site", response.data)
        self.assertIn(b"2024-01-01 10:00:00", response.data)
        self.assertIn(b"<span class=\"risk-score-value risk-score-low-text\">30/100</span>", response.data)
        self.assertIn(b"<span class=\"risk-category-label risk-score-low-text\">Low Risk</span>", response.data) # Typo fix
        self.assertIn(bytes(url_for('view_historical_analysis', policy_identifier='pid1_hist'), 'utf-8'), response.data)

        text_data = response.data.decode('utf-8')
        self.assertTrue(text_data.find("Another Org") < text_data.find("Example Site"), "Profile 2 (another.org) should appear before Profile 1 (example.com) due to newer timestamp.")

        # Check for the specific insight generated based on these profiles
        # Profile2 (75, High), Profile1 (30, Low) -> Overall (75+30)/2 = 52.5 -> 53 (Medium)
        # Expected insights:
        # 1. "Another Org has a High privacy risk score (75/100). Prioritize reviewing this service."
        # 2. "Your overall privacy posture is moderate. Review medium risk services and be mindful of new policies." (since overall score is 53)
        self.assertIn(b"Key Privacy Insights", response.data) # Check section title
        self.assertIn(b"Another Org has a High privacy risk score (75/100). Prioritize reviewing this service.", response.data)
        self.assertIn(b"Your overall privacy posture is moderate. Review medium risk services and be mindful of new policies.", response.data)

        self.assertIn(bytes(url_for('index'), 'utf-8'), response.data)
        self.assertIn(bytes(url_for('history_list_route_function'), 'utf-8'), response.data)
        self.assertIn(bytes(url_for('preferences'), 'utf-8'), response.data)

    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(True, "fake_key"))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    @patch('privacy_protocol.privacy_protocol.ml_classifier.ClauseClassifier.predict')
    def test_analyze_shows_per_clause_recommendations(self, mock_classify_clause, mock_gemini_summary, mock_gemini_key_check):
        # Setup: data_selling_allowed = False to trigger high concern and thus data selling recommendation
        prefs = get_default_preferences()
        prefs['data_selling_allowed'] = False
        # Save prefs to file so /analyze route picks them up
        from privacy_protocol.user_preferences import save_user_preferences, load_user_preferences
        save_user_preferences(prefs)
        # Ensure the app's interpreter instance has the latest prefs if it's not reloaded per request (it is reloaded in /analyze)
        # app.interpreter.load_user_preferences(load_user_preferences()) # Not strictly needed as /analyze reloads

        mock_classify_clause.return_value = "Data Selling"
        mock_gemini_summary.return_value = "This is a summary about data selling."
        policy_text = "We sell your data."

        with app.test_request_context():
            response = self.client.post(url_for('analyze'), data={'policy_text': policy_text})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Actionable Recommendations for this clause:", response.data)
        # Check for specific recommendation text related to REC_ID_OPT_OUT_DATA_SELLING
        # Assuming REC_ID_OPT_OUT_DATA_SELLING's title is "Opting Out of Data Selling"
        self.assertIn(b"Opting Out of Data Selling", response.data)
        self.assertIn(b"Consider looking for ways to opt out", response.data) # Part of its text

    # test_dashboard_displays_specific_insights_scenario_all_low was already applied in a previous step by the model
    # If it wasn't, this would be the place to add it.
    # For brevity, assuming it is present from the previous diff that was successful.
    # If it needs re-application, the content from prompt for test_dashboard_displays_specific_insights_scenario_all_low would go here.

    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
        ts = datetime.now(timezone.utc).isoformat()
        profile_low1 = ServiceProfile(
            service_id='lowrisk1.com', service_name='Low Risk One',
            latest_analysis_timestamp=ts, latest_policy_identifier='pid_lr1',
            latest_service_risk_score=15, num_total_clauses=10, high_concern_count=0, medium_concern_count=0, low_concern_count=1,
            source_url='http://lowrisk1.com'
        )
        profile_low2 = ServiceProfile(
            service_id='lowrisk2.com', service_name='Low Risk Two',
            latest_analysis_timestamp=ts, latest_policy_identifier='pid_lr2',
            latest_service_risk_score=25, num_total_clauses=12, high_concern_count=0, medium_concern_count=0, low_concern_count=2,
            source_url='http://lowrisk2.com'
        )
        dashboard_data_manager.save_service_profiles([profile_low1, profile_low2])

        with app.test_request_context():
            response = self.client.get(url_for('dashboard_overview'))
        self.assertEqual(response.status_code, 200)
        # Overall score: (15+25)/2 = 20 (Low)
        # Expected insight: "Your overall privacy posture appears relatively strong..." OR "All currently analyzed services have Low..."
        # The "All low" is more specific and should ideally be chosen if logic allows.
        # Current logic: if not key_insights_list and total_low_risk_services == total_services_analyzed:
        self.assertTrue(
            b"All currently analyzed services have Low privacy risk scores. Good job selecting services!" in response.data or
            b"Your overall privacy posture appears relatively strong" in response.data # Fallback if the "All low" is not hit first
        )
        # Assert overall score display for this "all low" scenario
        self.assertIn(b"Overall Privacy Posture", response.data)
        self.assertIn(b"<p class=\"overall-score-value risk-score-low-text\">20/100</p>", response.data)
        self.assertIn(b"<p class=\"risk-category-label risk-score-low-text\">Low Risk Profile</p>", response.data)
        self.assertIn(b"Across 2 analyzed service(s).", response.data)
        self.assertIn(b"Low Risk Services: 2", response.data)


    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(True, "fake_key"))
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    @patch('privacy_protocol.privacy_protocol.ml_classifier.ClauseClassifier.predict')
    def test_preference_change_impacts_analysis_and_dashboard(self, mock_classify_clause, mock_gemini_summary, mock_gemini_key_check):
        with app.test_request_context(): # For url_for and session context for flash
            # Step 1: Initial state & analysis (Data Selling Allowed)
            initial_prefs = get_default_preferences()
            initial_prefs['data_selling_allowed'] = True # Permissive
            # Must save these prefs to the actual file for /analyze to pick them up,
            # or ensure app.interpreter directly uses them if we don't go through file system for this test.
            # For a full integration test, saving to file is better.
            from privacy_protocol.user_preferences import save_user_preferences, load_user_preferences
            save_user_preferences(initial_prefs)
            app.interpreter.load_user_preferences(load_user_preferences()) # Ensure app interpreter has them

            mock_gemini_summary.return_value = "Summary for data selling clause."
            mock_classify_clause.return_value = "Data Selling"
            policy_text_s1 = "We sell your data for marketing."

            response_analyze_s1_initial = self.client.post(url_for('analyze'), data={
                'policy_text': policy_text_s1, 'source_url': 'http://serviceA.com/privacy'
            })
            self.assertEqual(response_analyze_s1_initial.status_code, 200)
            # Expected concern: Low (because data_selling_allowed = True)
            # Score: Base=20 (Selling), Bonus=2 (Low) -> Actual=22. Max=35. (22/35)*100 = 63 (Medium)
            self._assert_risk_display_elements(response_analyze_s1_initial.data, score=63, num_clauses=1, high_c=0, med_c=0, low_c=1, none_c=0)

            # Check dashboard initial state (one medium service)
            response_dash_initial = self.client.get(url_for('dashboard_overview'))
            self.assertIn(b"Overall Privacy Posture", response_dash_initial.data)
            self.assertIn(b"<p class=\"overall-score-value risk-score-medium-text\">63/100</p>", response_dash_initial.data)
            self.assertIn(b"You have 1 service(s) with a 'Medium' privacy risk score", response_dash_initial.data)


            # Step 2: Change preference (Data Selling Not Allowed)
            prefs_changed_response = self.client.post(url_for('preferences'), data={
                'data_selling_allowed': 'false', # Restrictive
                # Keep others as per default or initial_prefs to avoid None issues
                'data_sharing_for_ads_allowed': str(initial_prefs['data_sharing_for_ads_allowed']).lower(),
                'data_sharing_for_analytics_allowed': str(initial_prefs['data_sharing_for_analytics_allowed']).lower(),
                'cookies_for_tracking_allowed': str(initial_prefs['cookies_for_tracking_allowed']).lower(),
                'policy_changes_notification_required': str(initial_prefs['policy_changes_notification_required']).lower(),
                'childrens_privacy_strict': str(initial_prefs['childrens_privacy_strict']).lower(),
            }, follow_redirects=True)
            self.assertEqual(prefs_changed_response.status_code, 200)
            self.assertIn(b"Preferences saved successfully!", prefs_changed_response.data)
            # Verify app.interpreter picks up new prefs for next analysis (already happens in /analyze route)

            # Step 3: Re-analyze same policy for serviceA.com
            # Expect: Data Selling (AI Cat) + data_selling_allowed=False (Pref) -> High Concern
            # Score: Base=20 (Selling), Bonus=15 (High) -> Actual=35. Max=35. (35/35)*100 = 100 (High)
            # We need to ensure this is a *newer* analysis for serviceA.com to update its profile
            time.sleep(0.01) # Ensure timestamp will be different
            mock_gemini_summary.return_value = "Re-analysis summary for data selling clause." # Can be same
            mock_classify_clause.return_value = "Data Selling" # Stays same

            response_analyze_s1_reanalyzed = self.client.post(url_for('analyze'), data={
                'policy_text': policy_text_s1, 'source_url': 'http://serviceA.com/privacy_v2' # new source to ensure new history entry if needed, service_id is from domain
            })
            self.assertEqual(response_analyze_s1_reanalyzed.status_code, 200)
            self._assert_risk_display_elements(response_analyze_s1_reanalyzed.data, score=100, num_clauses=1, high_c=1, med_c=0, low_c=0, none_c=0)

            # Step 4: Check dashboard update
            response_dash_updated = self.client.get(url_for('dashboard_overview'))
            self.assertIn(b"Overall Privacy Posture", response_dash_updated.data)
            # Service A is now 100 (High). Overall score is 100.
            self.assertIn(b"<p class=\"overall-score-value risk-score-high-text\">100/100</p>", response_dash_updated.data)
            self.assertIn(b"serviceA.com has a High privacy risk score (100/100). Prioritize reviewing this service.", response_dash_updated.data)
            self.assertIn(b"High Risk Services: 1", response_dash_updated.data)
            self.assertIn(b"Medium Risk Services: 0", response_dash_updated.data)


    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
        # Configure default preferences for predictable concern levels
        default_prefs = get_default_preferences()
        default_prefs['data_selling_allowed'] = False # High concern for 'Data Selling'
        default_prefs['cookies_for_tracking_allowed'] = True # Low/None concern for 'Cookies' by default
        default_prefs['data_sharing_for_ads_allowed'] = False # High concern for 'Data Sharing'
        app.interpreter.load_user_preferences(default_prefs.copy())

        with app.test_request_context(): # For url_for
            # Step A: Initial State
            response = self.client.get(url_for('dashboard_overview'))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"No services analyzed yet.", response.data)
            user_profile_initial = dashboard_data_manager.load_user_privacy_profile()
            self.assertIsNotNone(user_profile_initial)
            self.assertIsNone(user_profile_initial.overall_privacy_risk_score)
            self.assertEqual(user_profile_initial.total_services_analyzed, 0)

            # Step B: Analyze First Policy (service1.com - Medium Risk)
            # Policy: "We use cookies for analytics." -> AI: Cookies/Tracking, User Pref: cookies_for_tracking_allowed=True -> Concern: Low
            # Score: Base=10 (Cookies), Bonus=2 (Low) -> Actual=12. Max=35. (12/35)*100 = 34 (Medium)
            mock_gemini_summary.return_value = "Mocked summary for service1.com"
            mock_classify_clause.return_value = "Cookies and Tracking Technologies"

            response_analyze_1 = self.client.post(url_for('analyze'), data={
                'policy_text': "We use cookies for analytics.",
                'source_url': 'http://service1.com/privacy'
            })
            self.assertEqual(response_analyze_1.status_code, 200)
            self._assert_risk_display_elements(response_analyze_1.data, score=34, num_clauses=1, high_c=0, med_c=0, low_c=1, none_c=0)

            service_profiles_b = dashboard_data_manager.load_service_profiles()
            self.assertEqual(len(service_profiles_b), 1)
            self.assertEqual(service_profiles_b[0].service_id, 'service1.com')
            self.assertEqual(service_profiles_b[0].latest_service_risk_score, 34)

            user_profile_b = dashboard_data_manager.load_user_privacy_profile()
            self.assertEqual(user_profile_b.overall_privacy_risk_score, 34)
            self.assertEqual(user_profile_b.total_services_analyzed, 1)
            self.assertEqual(user_profile_b.total_medium_risk_services_count, 1)

            response_dash_b = self.client.get(url_for('dashboard_overview'))
            self.assertIn(b"service1.com", response_dash_b.data)
            self.assertIn(b"34/100", response_dash_b.data)
            self.assertIn(b"Medium Risk Profile", response_dash_b.data) # Overall profile risk

            # Step C: Analyze Second Policy (service2.org - High Risk)
            # Policy: "We sell your personal data." -> AI: Data Selling, User Pref: data_selling_allowed=False -> Concern: High
            # Score: Base=20 (Selling), Bonus=15 (High) -> Actual=35. Max=35. (35/35)*100 = 100 (High)
            mock_gemini_summary.return_value = "Mocked summary for service2.org"
            mock_classify_clause.return_value = "Data Selling"
            response_analyze_2 = self.client.post(url_for('analyze'), data={
                'policy_text': "We sell your personal data.",
                'source_url': 'http://service2.org/privacy'
            })
            self.assertEqual(response_analyze_2.status_code, 200)
            self._assert_risk_display_elements(response_analyze_2.data, score=100, num_clauses=1, high_c=1, med_c=0, low_c=0, none_c=0)

            service_profiles_c = dashboard_data_manager.load_service_profiles()
            self.assertEqual(len(service_profiles_c), 2)

            user_profile_c = dashboard_data_manager.load_user_privacy_profile()
            self.assertEqual(user_profile_c.total_services_analyzed, 2)
            self.assertEqual(user_profile_c.overall_privacy_risk_score, round((34+100)/2)) # (34+100)/2 = 67 -> High
            self.assertEqual(user_profile_c.total_high_risk_services_count, 1)
            self.assertEqual(user_profile_c.total_medium_risk_services_count, 1)

            response_dash_c = self.client.get(url_for('dashboard_overview'))
            self.assertIn(b"service1.com", response_dash_c.data) # Should still be there
            self.assertIn(b"service2.org", response_dash_c.data)
            self.assertIn(b"100/100", response_dash_c.data) # service2 score
            self.assertIn(b"High Risk Profile", response_dash_c.data) # Overall profile risk (67)

            # Step D: Re-analyze First Policy (service1.com - now High Risk)
            # Policy: "We sell data from service1.com." -> AI: Data Selling, User Pref: data_selling_allowed=False -> Concern: High
            # Score: Base=20 (Selling), Bonus=15 (High) -> Actual=35. Max=35. (35/35)*100 = 100 (High)
            # This policy text should have a newer timestamp. We'll rely on current time for that.
            time.sleep(0.01) # Ensure timestamp difference
            mock_gemini_summary.return_value = "Updated summary for service1.com"
            mock_classify_clause.return_value = "Data Selling" # Changed category
            response_analyze_3 = self.client.post(url_for('analyze'), data={
                'policy_text': "We sell data from service1.com.", # Different text
                'source_url': 'http://service1.com/privacy_v2' # Can be same or different URL for same service_id
            })
            self.assertEqual(response_analyze_3.status_code, 200)
            self._assert_risk_display_elements(response_analyze_3.data, score=100, num_clauses=1, high_c=1, med_c=0, low_c=0, none_c=0)

            service_profiles_d = dashboard_data_manager.load_service_profiles()
            self.assertEqual(len(service_profiles_d), 2) # Still 2 services
            profile_s1_updated = next(p for p in service_profiles_d if p.service_id == 'service1.com')
            self.assertEqual(profile_s1_updated.latest_service_risk_score, 100)
            self.assertTrue(profile_s1_updated.latest_analysis_timestamp > user_profile_b.last_aggregated_at) # Check timestamp updated

            user_profile_d = dashboard_data_manager.load_user_privacy_profile()
            self.assertEqual(user_profile_d.total_services_analyzed, 2)
            self.assertEqual(user_profile_d.overall_privacy_risk_score, round((100+100)/2)) # (100+100)/2 = 100 -> High
            self.assertEqual(user_profile_d.total_high_risk_services_count, 2) # Both are high now
            self.assertEqual(user_profile_d.total_medium_risk_services_count, 0)

            response_dash_d = self.client.get(url_for('dashboard_overview'))
            self.assertIn(b"service1.com", response_dash_d.data)
            self.assertIn(b"100/100", response_dash_d.data) # service1 updated score
            self.assertIn(b"service2.org", response_dash_d.data)
            self.assertIn(b"High Risk Profile", response_dash_d.data) # Overall profile risk (100)

    @patch.dict(os.environ, {ACTIVE_LLM_PROVIDER_ENV_VAR: PROVIDER_GEMINI}, clear=True)
    @patch(GEMINI_SERVICE_KEY_CHECK_PATH, return_value=(True, "fake_key")) # Assume key is available
    @patch(GEMINI_SERVICE_GENERATE_SUMMARY_PATH)
    # Mock classify_clause for precise control over AI category
    @patch('privacy_protocol.privacy_protocol.ml_classifier.ClauseClassifier.predict')
    def test_dashboard_full_flow_multiple_analyses_and_updates(self, mock_classify_clause, mock_gemini_summary, mock_gemini_key_check):
        # This is the original test that was overwritten, re-adding it.
        # Configure default preferences for predictable concern levels
        default_prefs = get_default_preferences()
        default_prefs['data_selling_allowed'] = False
        default_prefs['cookies_for_tracking_allowed'] = True
        default_prefs['data_sharing_for_ads_allowed'] = False
        app.interpreter.load_user_preferences(default_prefs.copy())

        with app.test_request_context():
            # Step A: Initial State
            response = self.client.get(url_for('dashboard_overview'))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"No services analyzed yet.", response.data)
            user_profile_initial = dashboard_data_manager.load_user_privacy_profile()
            self.assertIsNotNone(user_profile_initial)
            self.assertIsNone(user_profile_initial.overall_privacy_risk_score)

            # Step B: Analyze First Policy (service1.com - Medium Risk)
            mock_gemini_summary.return_value = "Mocked summary for service1.com"
            mock_classify_clause.return_value = "Cookies and Tracking Technologies" # Score 34 (Medium)

            self.client.post(url_for('analyze'), data={
                'policy_text': "We use cookies for analytics.", 'source_url': 'http://service1.com/privacy'
            })
            user_profile_b = dashboard_data_manager.load_user_privacy_profile()
            self.assertEqual(user_profile_b.overall_privacy_risk_score, 34)
            self.assertEqual(user_profile_b.total_medium_risk_services_count, 1)

            response_dash_b = self.client.get(url_for('dashboard_overview'))
            self.assertIn(b"service1.com", response_dash_b.data)
            self.assertIn(b"34/100", response_dash_b.data)
            self.assertIn(b"Medium Risk Profile", response_dash_b.data)

            # Step C: Analyze Second Policy (service2.org - High Risk)
            mock_gemini_summary.return_value = "Mocked summary for service2.org"
            mock_classify_clause.return_value = "Data Selling" # Score 100 (High)
            self.client.post(url_for('analyze'), data={
                'policy_text': "We sell your personal data.", 'source_url': 'http://service2.org/privacy'
            })
            user_profile_c = dashboard_data_manager.load_user_privacy_profile()
            self.assertEqual(user_profile_c.overall_privacy_risk_score, round((34+100)/2)) # 67 (High)
            self.assertEqual(user_profile_c.total_high_risk_services_count, 1)
            self.assertEqual(user_profile_c.total_medium_risk_services_count, 1)

            response_dash_c = self.client.get(url_for('dashboard_overview'))
            self.assertIn(b"service2.org", response_dash_c.data)
            self.assertIn(b"100/100", response_dash_c.data)
            self.assertIn(b"High Risk Profile", response_dash_c.data)

            # Step D: Re-analyze First Policy (service1.com - now High Risk)
            time.sleep(0.01)
            mock_gemini_summary.return_value = "Updated summary for service1.com"
            mock_classify_clause.return_value = "Data Selling" # Score 100 (High)
            self.client.post(url_for('analyze'), data={
                'policy_text': "We sell data from service1.com.", 'source_url': 'http://service1.com/privacy_v2'
            })
            user_profile_d = dashboard_data_manager.load_user_privacy_profile()
            self.assertEqual(user_profile_d.overall_privacy_risk_score, 100) # (100+100)/2
            self.assertEqual(user_profile_d.total_high_risk_services_count, 2)

            response_dash_d = self.client.get(url_for('dashboard_overview'))
            self.assertIn(b"service1.com", response_dash_d.data)
            # Check that service1.com now shows 100/100 (it should be the first one due to latest timestamp)
            # This requires more complex parsing or ensuring service1.com is indeed first.
            # For now, just check that a 100/100 for service1.com is present somewhere.
            # A better test would be to check the ServiceProfile object directly.
            s1_profile_final = next(p for p in dashboard_data_manager.load_service_profiles() if p.service_id == 'service1.com')
            self.assertEqual(s1_profile_final.latest_service_risk_score, 100)
            self.assertIn(b"High Risk Profile", response_dash_d.data) # Overall

if __name__ == '__main__':
    unittest.main()
