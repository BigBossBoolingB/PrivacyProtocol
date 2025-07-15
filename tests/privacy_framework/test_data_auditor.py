import os
import shutil
import unittest
import json
from src.privacy_framework.data_auditor import DataTransformationAuditor

class TestDataTransformationAuditor(unittest.TestCase):

    def setUp(self):
        self.log_file_path = "_test_audit_log.jsonl"
        self.auditor = DataTransformationAuditor(log_file_path=self.log_file_path)

    def tearDown(self):
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

    def test_log_event(self):
        self.auditor.log_event(
            event_type="test_event",
            original_data={"key": "value"},
            transformed_data={"key": "new_value"},
            policy_id="test_policy",
            consent_id="test_consent",
            outcome="success"
        )
        self.assertTrue(os.path.exists(self.log_file_path))
        with open(self.log_file_path, "r") as f:
            log_entry = json.loads(f.readline())
            self.assertEqual(log_entry["event_type"], "test_event")
            self.assertIsNotNone(log_entry["log_hash"])

if __name__ == '__main__':
    unittest.main()
