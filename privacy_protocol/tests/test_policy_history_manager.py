import unittest
import os
import json
import shutil
import time
from datetime import timezone, datetime
from unittest.mock import patch, MagicMock # Added

# Add project root to sys.path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from privacy_protocol import policy_history_manager # Import the module directly

class TestPolicyHistoryManager(unittest.TestCase):
    def setUp(self):
        self.history_dir = policy_history_manager.POLICY_HISTORY_DIR
        # Ensure a clean state for POLICY_HISTORY_DIR before each test
        if os.path.exists(self.history_dir):
            shutil.rmtree(self.history_dir)
        # _ensure_history_dir_exists is called by save functions, but good to have it for list/get too if dir might be missing
        policy_history_manager._ensure_history_dir_exists()

    def tearDown(self):
        if os.path.exists(self.history_dir):
            shutil.rmtree(self.history_dir)

    def _create_dummy_analysis_data(self, text_suffix=""):
        # More closely match the structure saved by app.py
        return {
            'policy_text': f"Sample policy text {text_suffix}",
            'analysis_results': [
                {
                    'clause_text': f"Clause 1 {text_suffix}",
                    'ai_category': 'Data Collection',
                    'plain_language_summary': 'This is about collecting data.',
                    'user_concern_level': 'Low',
                    'keyword_matches': [],
                    'recommendations': []
                }
            ],
            'risk_assessment': {'overall_risk_score': 10 if text_suffix else 5, 'high_concern_count':1, 'medium_concern_count':0, 'low_concern_count':0, 'none_concern_count':0},
            'source_url': f'http://example.com/policy{text_suffix}' if text_suffix else 'pasted text'
        }

    def test_generate_policy_identifier_is_timestamp_string(self):
        identifier1 = policy_history_manager.generate_policy_identifier()
        time.sleep(0.001)
        identifier2 = policy_history_manager.generate_policy_identifier()
        self.assertIsInstance(identifier1, str)
        self.assertTrue(len(identifier1) >= 17) # YYYYMMDDHHMMSSms -> 14 + 3 = 17
        self.assertNotEqual(identifier1, identifier2)
        self.assertTrue(identifier1.isdigit()) # Should be all digits

    def test_save_and_get_policy_analysis(self):
        data = self._create_dummy_analysis_data("save_test")
        identifier = policy_history_manager.generate_policy_identifier()

        filename = policy_history_manager.save_policy_analysis(
            identifier, data['policy_text'], data['analysis_results'],
            data['risk_assessment'], data['source_url']
        )
        self.assertIsNotNone(filename)
        self.assertEqual(filename, f"{identifier}.json")
        filepath = os.path.join(self.history_dir, filename)
        self.assertTrue(os.path.exists(filepath))

        loaded_data = policy_history_manager.get_policy_analysis(identifier)
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data['policy_identifier'], identifier)
        self.assertEqual(loaded_data['full_policy_text'], data['policy_text'])
        self.assertEqual(loaded_data['analysis_results'], data['analysis_results'])
        self.assertEqual(loaded_data['risk_assessment'], data['risk_assessment'])
        self.assertEqual(loaded_data['source_url'], data['source_url'])
        self.assertIn('analysis_timestamp', loaded_data)
        # Check if timestamp is a valid ISO format string
        dt_obj = datetime.fromisoformat(loaded_data['analysis_timestamp'].replace('Z', '+00:00'))
        self.assertEqual(dt_obj.tzinfo, timezone.utc)


    def test_get_policy_analysis_not_found(self):
        loaded_data = policy_history_manager.get_policy_analysis("non_existent_id_123")
        self.assertIsNone(loaded_data)

    def test_list_analyzed_policies(self):
        num_policies = 3
        saved_ids = []
        for i in range(num_policies):
            data = self._create_dummy_analysis_data(f"policy{i}")
            identifier = policy_history_manager.generate_policy_identifier()
            policy_history_manager.save_policy_analysis(
                identifier, data['policy_text'], data['analysis_results'],
                data['risk_assessment'], data['source_url']
            )
            saved_ids.append(identifier)
            if i < num_policies - 1:
                 time.sleep(0.001) # Ensure distinct timestamps

        listed_policies = policy_history_manager.list_analyzed_policies()
        self.assertEqual(len(listed_policies), num_policies)

        # Check if sorted by timestamp descending (last saved should be first)
        self.assertEqual(listed_policies[0]['identifier'], saved_ids[-1])
        self.assertEqual(listed_policies[-1]['identifier'], saved_ids[0])

        for item in listed_policies:
            self.assertIn('identifier', item)
            self.assertIn('timestamp', item)
            self.assertIn('source_url', item)

    def test_list_analyzed_policies_empty(self):
        listed_policies = policy_history_manager.list_analyzed_policies()
        self.assertEqual(len(listed_policies), 0)

    def test_get_latest_policy_analysis(self):
        self.assertIsNone(policy_history_manager.get_latest_policy_analysis(), "Should be None when no policies exist.")

        data1 = self._create_dummy_analysis_data("latest1")
        id1 = policy_history_manager.generate_policy_identifier()
        policy_history_manager.save_policy_analysis(id1, data1['policy_text'], data1['analysis_results'], data1['risk_assessment'], data1['source_url'])
        time.sleep(0.001)

        data2 = self._create_dummy_analysis_data("latest2") # This one is later
        id2 = policy_history_manager.generate_policy_identifier()
        policy_history_manager.save_policy_analysis(id2, data2['policy_text'], data2['analysis_results'], data2['risk_assessment'], data2['source_url'])

        latest = policy_history_manager.get_latest_policy_analysis()
        self.assertIsNotNone(latest)
        self.assertEqual(latest['policy_identifier'], id2)
        self.assertEqual(latest['full_policy_text'], data2['policy_text'])

    def test_corrupted_json_file_in_history(self):
        # Save one good policy
        data_good = self._create_dummy_analysis_data("good")
        id_good = policy_history_manager.generate_policy_identifier()
        policy_history_manager.save_policy_analysis(id_good, data_good['policy_text'], data_good['analysis_results'], data_good['risk_assessment'])

        # Create a corrupted JSON file
        corrupted_file_path = os.path.join(self.history_dir, "corrupted.json")
        with open(corrupted_file_path, 'w') as f:
            f.write("this is not valid json {")

        # Create another good policy file after the corrupted one
        time.sleep(0.001)
        data_good2 = self._create_dummy_analysis_data("good2")
        id_good2 = policy_history_manager.generate_policy_identifier()
        policy_history_manager.save_policy_analysis(id_good2, data_good2['policy_text'], data_good2['analysis_results'], data_good2['risk_assessment'])


        # list_analyzed_policies should skip the corrupted file and return the good ones
        with patch('sys.stdout', new_callable=MagicMock) as mock_stdout: # Suppress print from error
            listed_policies = policy_history_manager.list_analyzed_policies()
            self.assertEqual(len(listed_policies), 2) # Should only list the two good ones
            # Check that error was printed for corrupted file
            self.assertTrue(any("Error reading or parsing policy file" in call_args[0][0] for call_args in mock_stdout.write.call_args_list if call_args[0]))


        # get_policy_analysis for corrupted file should return None
        with patch('sys.stdout', new_callable=MagicMock) as mock_stdout_get:
            corrupted_data = policy_history_manager.get_policy_analysis("corrupted") # Try to load by identifier
            self.assertIsNone(corrupted_data)
            self.assertTrue(any("Error loading policy analysis" in call_args[0][0] for call_args in mock_stdout_get.write.call_args_list if call_args[0]))


if __name__ == '__main__':
    unittest.main()
