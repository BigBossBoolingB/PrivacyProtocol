import unittest
import os
import json
import shutil
import time # For timestamp differentiation
from datetime import datetime, timezone # For timestamp generation
from unittest.mock import patch, mock_open, MagicMock # Added MagicMock
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Modules to test
from privacy_protocol.privacy_protocol import dashboard_data_manager
from privacy_protocol.privacy_protocol.dashboard_models import ServiceProfile, UserPrivacyProfile # Import UserPrivacyProfile

class TestDashboardDataManager(unittest.TestCase):
    def setUp(self):
        self.user_data_dir = dashboard_data_manager.USER_DATA_DIR
        self.profiles_path = dashboard_data_manager.SERVICE_PROFILES_PATH
        self.user_profile_path = dashboard_data_manager.USER_PRIVACY_PROFILE_PATH # Added for cleanup

        # Ensure a clean state for USER_DATA_DIR before each test
        if os.path.exists(self.user_data_dir):
            shutil.rmtree(self.user_data_dir)
        os.makedirs(self.user_data_dir)

    def tearDown(self):
        if os.path.exists(self.user_data_dir):
            shutil.rmtree(self.user_data_dir)
        # Redundant if user_data_dir is rmtree'd, but good for explicitness if that changes
        # if os.path.exists(self.profiles_path):
        #     os.remove(self.profiles_path)
        # if os.path.exists(self.user_profile_path):
        #     os.remove(self.user_profile_path)


    def test_user_privacy_profile_dataclass_defaults(self):
        profile = UserPrivacyProfile()
        self.assertEqual(profile.user_id, "default_user")
        self.assertIsNone(profile.overall_privacy_risk_score)
        self.assertEqual(profile.key_privacy_insights, [])
        self.assertEqual(profile.total_services_analyzed, 0)
        self.assertEqual(profile.total_high_risk_services_count, 0)
        self.assertEqual(profile.total_medium_risk_services_count, 0)
        self.assertEqual(profile.total_low_risk_services_count, 0)
        self.assertIsNone(profile.last_aggregated_at)

        # Test __post_init__ for score clamping
        profile_high = UserPrivacyProfile(overall_privacy_risk_score=120)
        self.assertEqual(profile_high.overall_privacy_risk_score, 100)
        profile_low = UserPrivacyProfile(overall_privacy_risk_score=-10)
        self.assertEqual(profile_low.overall_privacy_risk_score, 0)
        profile_valid = UserPrivacyProfile(overall_privacy_risk_score=50)
        self.assertEqual(profile_valid.overall_privacy_risk_score, 50)


    def test_get_service_id_from_source_url(self):
        sid, sname = dashboard_data_manager.get_service_id_from_source('http://example.com/privacy', 'pid1')
        self.assertEqual(sid, 'example.com')
        self.assertEqual(sname, 'example.com')

        sid, sname = dashboard_data_manager.get_service_id_from_source('https://www.sub.example.co.uk/path?query=1', 'pid2')
        self.assertEqual(sid, 'sub.example.co.uk')
        self.assertEqual(sname, 'sub.example.co.uk')

    def test_get_service_id_from_source_pasted_text(self):
        sid, sname = dashboard_data_manager.get_service_id_from_source('Pasted Text Input', 'policy12345')
        self.assertEqual(sid, 'policy12345')
        self.assertEqual(sname, 'Pasted Analysis (policy12345)')

    def test_get_service_id_from_source_empty_url(self):
        sid, sname = dashboard_data_manager.get_service_id_from_source('', 'policy12345')
        self.assertEqual(sid, 'policy12345')
        self.assertEqual(sname, 'Pasted Analysis (policy12345)')

    def test_load_service_profiles_no_file(self):
        profiles = dashboard_data_manager.load_service_profiles()
        self.assertEqual(profiles, [])

    def test_load_service_profiles_empty_file(self):
        with open(self.profiles_path, 'w') as f:
            json.dump([], f)
        profiles = dashboard_data_manager.load_service_profiles()
        self.assertEqual(profiles, [])

    def test_save_and_load_service_profiles_valid_data(self):
        ts = datetime.now(timezone.utc).isoformat()
        profile_list = [
            ServiceProfile('id1', 'Service 1', ts, 'pid1', 50, 10, 1, 2, 3, 'http://s1.com'),
            ServiceProfile('id2', 'Service 2', ts, 'pid2', 70, 20, 2, 3, 4, 'http://s2.com')
        ]
        dashboard_data_manager.save_service_profiles(profile_list)
        self.assertTrue(os.path.exists(self.profiles_path))

        loaded_profiles = dashboard_data_manager.load_service_profiles()
        self.assertEqual(len(loaded_profiles), 2)
        self.assertIsInstance(loaded_profiles[0], ServiceProfile)
        self.assertEqual(loaded_profiles[0].service_id, 'id1')
        self.assertEqual(loaded_profiles[1].service_name, 'Service 2')

    def test_load_service_profiles_corrupted_json(self):
        with open(self.profiles_path, 'w') as f:
            f.write("this is not json[")
        # Suppress print for this expected error
        with patch('sys.stdout', new_callable=MagicMock):
            profiles = dashboard_data_manager.load_service_profiles()
        self.assertEqual(profiles, [])

    def _create_sample_policy_analysis_data(self, p_id, source_url, timestamp_str, score, clauses=10, h=1,m=1,l=1, n=0): # Added none_concern_count
        return {
            'policy_identifier': p_id,
            'source_url': source_url,
            'analysis_timestamp': timestamp_str,
            'full_policy_text': 'text',
            'analysis_results': [],
            'risk_assessment': {
                'service_risk_score': score, 'num_clauses_analyzed': clauses,
                'high_concern_count': h, 'medium_concern_count': m, 'low_concern_count': l,
                'none_concern_count': n # Added
            }
        }

    def test_update_or_create_service_profile_new_url_service(self):
        ts1 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        analysis_data = self._create_sample_policy_analysis_data('pid_ex1', 'http://example.com', ts1, 60)
        dashboard_data_manager.update_or_create_service_profile(analysis_data)

        profiles = dashboard_data_manager.load_service_profiles()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].service_id, 'example.com')
        self.assertEqual(profiles[0].service_name, 'example.com')
        self.assertEqual(profiles[0].latest_service_risk_score, 60)
        self.assertEqual(profiles[0].latest_policy_identifier, 'pid_ex1')

    def test_update_or_create_service_profile_new_pasted_text_service(self):
        ts1 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        analysis_data = self._create_sample_policy_analysis_data('ts_id_001', 'Pasted Text Input', ts1, 40)
        dashboard_data_manager.update_or_create_service_profile(analysis_data)

        profiles = dashboard_data_manager.load_service_profiles()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].service_id, 'ts_id_001') # Uses policy_id as service_id for pasted
        self.assertEqual(profiles[0].service_name, 'Pasted Analysis (ts_id_001)')
        self.assertEqual(profiles[0].latest_service_risk_score, 40)

    def test_update_or_create_service_profile_update_existing_with_newer(self):
        ts1 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        analysis1 = self._create_sample_policy_analysis_data('pid_ex1_v1', 'http://example.com', ts1, 60)
        dashboard_data_manager.update_or_create_service_profile(analysis1)

        time.sleep(0.001) # ensure timestamp is different enough if tests run fast
        ts2 = datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc).isoformat()
        analysis2 = self._create_sample_policy_analysis_data('pid_ex1_v2', 'http://example.com/privacy', ts2, 75)
        dashboard_data_manager.update_or_create_service_profile(analysis2)

        profiles = dashboard_data_manager.load_service_profiles()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].service_id, 'example.com')
        self.assertEqual(profiles[0].latest_service_risk_score, 75)
        self.assertEqual(profiles[0].latest_policy_identifier, 'pid_ex1_v2')
        self.assertEqual(profiles[0].latest_analysis_timestamp, ts2)

    def test_update_or_create_service_profile_attempt_update_with_older(self):
        ts2 = datetime(2024, 1, 1, 11, 0, 0, tzinfo=timezone.utc).isoformat()
        analysis2 = self._create_sample_policy_analysis_data('pid_ex1_v2', 'http://example.com', ts2, 75)
        dashboard_data_manager.update_or_create_service_profile(analysis2)

        ts1 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        analysis1 = self._create_sample_policy_analysis_data('pid_ex1_v1', 'http://example.com/privacy', ts1, 60)
        dashboard_data_manager.update_or_create_service_profile(analysis1) # Attempt to update with older

        profiles = dashboard_data_manager.load_service_profiles()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].service_id, 'example.com')
        self.assertEqual(profiles[0].latest_service_risk_score, 75) # Should remain 75 (from newer analysis2)
        self.assertEqual(profiles[0].latest_policy_identifier, 'pid_ex1_v2')
        self.assertEqual(profiles[0].latest_analysis_timestamp, ts2)

    def test_get_all_service_profiles_for_dashboard_sorting(self):
        # Save profiles with different timestamps
        ts1 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        analysis1 = self._create_sample_policy_analysis_data('p1', 'http://service_a.com', ts1, 50)
        dashboard_data_manager.update_or_create_service_profile(analysis1)
        time.sleep(0.001)

        ts3 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat() # newest
        analysis3 = self._create_sample_policy_analysis_data('p3', 'http://service_c.com', ts3, 60)
        dashboard_data_manager.update_or_create_service_profile(analysis3)
        time.sleep(0.001)

        ts2 = datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone.utc).isoformat() # oldest
        analysis2 = self._create_sample_policy_analysis_data('p2', 'http://service_b.com', ts2, 40)
        dashboard_data_manager.update_or_create_service_profile(analysis2)

        dashboard_profiles = dashboard_data_manager.get_all_service_profiles_for_dashboard()
        self.assertEqual(len(dashboard_profiles), 3)
        # Expected order: p3 (newest), p1, p2 (oldest)
        self.assertEqual(dashboard_profiles[0].service_id, 'service_c.com')
        self.assertEqual(dashboard_profiles[1].service_id, 'service_a.com')
        self.assertEqual(dashboard_profiles[2].service_id, 'service_b.com')

    def test_calculate_and_save_user_profile_no_services(self):
        # Ensure service_profiles.json is empty or non-existent
        if os.path.exists(self.profiles_path):
            os.remove(self.profiles_path)

        profile = dashboard_data_manager.calculate_and_save_user_privacy_profile()
        self.assertIsNotNone(profile)
        self.assertIsNone(profile.overall_privacy_risk_score) # As per current logic for no services
        self.assertEqual(profile.total_services_analyzed, 0)
        self.assertIn("No services analyzed yet.", profile.key_privacy_insights)
        self.assertTrue(os.path.exists(self.user_profile_path))
        with open(self.user_profile_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['overall_privacy_risk_score'], None)
        self.assertEqual(data['total_services_analyzed'], 0)

    def test_calculate_and_save_user_profile_one_service(self):
        ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat()
        service1_data = ServiceProfile(
            service_id='s1.com', service_name='Service 1',
            latest_analysis_timestamp=ts, latest_policy_identifier='pid_s1',
            latest_service_risk_score=70, num_total_clauses=10,
            high_concern_count=3, medium_concern_count=0, low_concern_count=0, # Counts for ServiceProfile
            source_url='http://s1.com'
        )
        dashboard_data_manager.save_service_profiles([service1_data])

        user_profile = dashboard_data_manager.calculate_and_save_user_privacy_profile()
        self.assertIsNotNone(user_profile)
        self.assertEqual(user_profile.total_services_analyzed, 1)
        self.assertEqual(user_profile.overall_privacy_risk_score, 70)
        self.assertEqual(user_profile.total_high_risk_services_count, 1)
        self.assertEqual(user_profile.total_medium_risk_services_count, 0)
        self.assertEqual(user_profile.total_low_risk_services_count, 0)
        self.assertIn("Service 1 has a High privacy risk score (70/100). Review its details.", user_profile.key_privacy_insights)
        self.assertTrue(os.path.exists(self.user_profile_path))

    def test_calculate_and_save_user_profile_multiple_services_average_score(self):
        ts = datetime.now(timezone.utc).isoformat()
        services_data = [
            ServiceProfile('s1.com', 'S1', ts, 'p1', 30, 10,0,0,1), # Low
            ServiceProfile('s2.com', 'S2', ts, 'p2', 60, 10,0,1,0), # Medium
            ServiceProfile('s3.com', 'S3', ts, 'p3', 90, 10,1,0,0)  # High
        ]
        dashboard_data_manager.save_service_profiles(services_data)

        user_profile = dashboard_data_manager.calculate_and_save_user_privacy_profile()
        self.assertIsNotNone(user_profile)
        self.assertEqual(user_profile.total_services_analyzed, 3)
        self.assertEqual(user_profile.overall_privacy_risk_score, round((30+60+90)/3)) # Avg = 60
        self.assertEqual(user_profile.total_low_risk_services_count, 1)
        self.assertEqual(user_profile.total_medium_risk_services_count, 1)
        self.assertEqual(user_profile.total_high_risk_services_count, 1)
        self.assertIn("S3 has a High privacy risk score (90/100). Review its details.", user_profile.key_privacy_insights)

    def test_calculate_and_save_user_profile_insight_generation_logic(self):
        ts = datetime.now(timezone.utc).isoformat()
        # Scenario 1: All low risk
        services_low = [ServiceProfile('low1.com', 'Low1', ts, 'pl1', 20, 5,0,0,1)]
        dashboard_data_manager.save_service_profiles(services_low)
        profile_low = dashboard_data_manager.calculate_and_save_user_privacy_profile()
        self.assertIn("Your overall privacy posture appears relatively strong based on analyzed services.", profile_low.key_privacy_insights)

        # Scenario 2: Mix with one high risk
        if os.path.exists(self.profiles_path): os.remove(self.profiles_path) # Clean for next scenario
        services_high = [
            ServiceProfile('low2.com', 'Low2', ts, 'pl2', 20, 5,0,0,1),
            ServiceProfile('high1.com', 'High1', ts, 'ph1', 80, 5,1,0,0)
        ]
        dashboard_data_manager.save_service_profiles(services_high)
        profile_high = dashboard_data_manager.calculate_and_save_user_privacy_profile()
        self.assertIn("High1 has a High privacy risk score (80/100). Review its details.", profile_high.key_privacy_insights)

        # Scenario 3: No high risk, but overall medium
        if os.path.exists(self.profiles_path): os.remove(self.profiles_path)
        services_medium = [
            ServiceProfile('med1.com', 'Med1', ts, 'pm1', 50, 5,0,1,0),
            ServiceProfile('med2.com', 'Med2', ts, 'pm2', 60, 5,0,1,0)
        ]
        dashboard_data_manager.save_service_profiles(services_medium)
        profile_medium = dashboard_data_manager.calculate_and_save_user_privacy_profile()
        self.assertIn("Review individual service risk scores to understand your privacy posture.", profile_medium.key_privacy_insights)


    def test_load_user_privacy_profile_no_file_triggers_calculation(self):
        if os.path.exists(self.user_profile_path):
            os.remove(self.user_profile_path)

        mock_profile_data = UserPrivacyProfile(overall_privacy_risk_score=55)
        with patch('privacy_protocol.privacy_protocol.dashboard_data_manager.calculate_and_save_user_privacy_profile', return_value=mock_profile_data) as mock_calc:
            loaded_profile = dashboard_data_manager.load_user_privacy_profile()
            mock_calc.assert_called_once()
            self.assertEqual(loaded_profile.overall_privacy_risk_score, 55)

    def test_load_user_privacy_profile_valid_file(self):
        ts = datetime.now(timezone.utc).isoformat()
        profile_data = {
            "user_id": "test_user", "overall_privacy_risk_score": 42,
            "key_privacy_insights": ["Test insight"], "total_services_analyzed": 1,
            "total_high_risk_services_count": 0, "total_medium_risk_services_count": 1,
            "total_low_risk_services_count": 0, "last_aggregated_at": ts
        }
        with open(self.user_profile_path, 'w') as f:
            json.dump(profile_data, f)

        loaded_profile = dashboard_data_manager.load_user_privacy_profile(user_id="test_user")
        self.assertIsNotNone(loaded_profile)
        self.assertEqual(loaded_profile.overall_privacy_risk_score, 42)
        self.assertIn("Test insight", loaded_profile.key_privacy_insights)

    def test_load_user_privacy_profile_corrupted_file_triggers_recalculation(self):
        with open(self.user_profile_path, 'w') as f:
            f.write("this is not json")

        mock_rebuilt_profile = UserPrivacyProfile(overall_privacy_risk_score=77) # Expected from rebuild
        # Ensure service profiles are empty so rebuild is predictable (no services analyzed)
        if os.path.exists(self.profiles_path):
            os.remove(self.profiles_path)

        with patch('privacy_protocol.privacy_protocol.dashboard_data_manager.calculate_and_save_user_privacy_profile', return_value=mock_rebuilt_profile) as mock_recalc:
            loaded_profile = dashboard_data_manager.load_user_privacy_profile()
            mock_recalc.assert_called_once() # Should be called due to corruption
            self.assertEqual(loaded_profile.overall_privacy_risk_score, 77)


if __name__ == '__main__':
    unittest.main()
