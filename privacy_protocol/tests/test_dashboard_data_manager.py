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
from privacy_protocol.privacy_protocol.dashboard_models import ServiceProfile

class TestDashboardDataManager(unittest.TestCase):
    def setUp(self):
        self.user_data_dir = dashboard_data_manager.USER_DATA_DIR
        self.profiles_path = dashboard_data_manager.SERVICE_PROFILES_PATH
        # Ensure a clean state for USER_DATA_DIR before each test
        if os.path.exists(self.user_data_dir):
            shutil.rmtree(self.user_data_dir)
        os.makedirs(self.user_data_dir)

    def tearDown(self):
        if os.path.exists(self.user_data_dir):
            shutil.rmtree(self.user_data_dir)

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

if __name__ == '__main__':
    unittest.main()
