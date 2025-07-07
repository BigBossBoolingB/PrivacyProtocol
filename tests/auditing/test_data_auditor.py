import unittest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import uuid
import hashlib

from privacy_protocol_core.auditing.data_auditor import DataTransformationAuditor

class TestDataTransformationAuditor(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.auditor = DataTransformationAuditor(log_dir_path=str(self.test_dir))

        # Sample data for hashing
        self.sample_data1 = {"field1": "value1", "field2": 123}
        self.sample_data2 = {"name": "Alice", "age": 30}
        self.hash1 = DataTransformationAuditor.hash_data(self.sample_data1)
        self.hash2 = DataTransformationAuditor.hash_data(self.sample_data2)


    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_log_dir_creation(self):
        self.assertTrue(self.auditor.log_dir_path.exists())
        self.assertTrue(self.auditor.log_dir_path.is_dir())

    def test_hash_data_consistency(self):
        data = {"b": 2, "a": 1}
        data_reordered = {"a": 1, "b": 2}
        self.assertEqual(DataTransformationAuditor.hash_data(data), DataTransformationAuditor.hash_data(data_reordered))
        self.assertNotEqual(DataTransformationAuditor.hash_data(data), DataTransformationAuditor.hash_data({"a":1, "b":3}))

    def test_log_event_creates_file_and_writes_entry(self):
        self.assertFalse(self.auditor.audit_log_file.exists())

        success = self.auditor.log_event(
            event_type="TEST_EVENT_1", user_id="userA", policy_id="polX", policy_version="1.0",
            consent_id="con1", input_data_hash=self.hash1, output_data_hash=self.hash2,
            transformation_details={"field1": "transformed"}, status="Transformed"
        )
        self.assertTrue(success)
        self.assertTrue(self.auditor.audit_log_file.exists())

        with open(self.auditor.audit_log_file, 'r') as f:
            line = f.readline()
            entry = json.loads(line)

        self.assertEqual(entry["event_type"], "TEST_EVENT_1")
        self.assertEqual(entry["user_id"], "userA")
        self.assertEqual(entry["input_data_hash"], self.hash1)
        self.assertEqual(entry["output_data_hash"], self.hash2)
        self.assertEqual(entry["status"], "Transformed")
        self.assertIsNone(entry["previous_log_hash"]) # First entry
        self.assertIsNotNone(entry["current_entry_hash"])
        self.assertEqual(self.auditor.last_log_hash, entry["current_entry_hash"])


    def test_log_chaining(self):
        # Log first event
        self.auditor.log_event("EVT1", "u1", "p1", "1.0", "c1", "h_in1", "h_out1", {}, "OK1")
        hash_of_evt1 = self.auditor.last_log_hash
        self.assertIsNotNone(hash_of_evt1)

        # Log second event
        self.auditor.log_event("EVT2", "u2", "p2", "1.1", "c2", "h_in2", "h_out2", {}, "OK2")
        hash_of_evt2 = self.auditor.last_log_hash
        self.assertIsNotNone(hash_of_evt2)
        self.assertNotEqual(hash_of_evt1, hash_of_evt2)

        with open(self.auditor.audit_log_file, 'r') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 2)

        entry1_data = json.loads(lines[0])
        entry2_data = json.loads(lines[1])

        self.assertIsNone(entry1_data["previous_log_hash"])
        self.assertEqual(entry1_data["current_entry_hash"], hash_of_evt1)

        self.assertEqual(entry2_data["previous_log_hash"], hash_of_evt1)
        self.assertEqual(entry2_data["current_entry_hash"], hash_of_evt2)

    def test_get_last_log_hash_on_existing_file(self):
        # Log some events
        self.auditor.log_event("E1", "u", "p", "1", "c", "h1", "h1o", {}, "S1")
        last_hash_after_e1 = self.auditor.last_log_hash
        self.auditor.log_event("E2", "u", "p", "1", "c", "h2", "h2o", {}, "S2")
        last_hash_after_e2 = self.auditor.last_log_hash

        # Create new auditor instance for the same directory
        new_auditor = DataTransformationAuditor(log_dir_path=str(self.test_dir))
        self.assertEqual(new_auditor.last_log_hash, last_hash_after_e2,
                         "New auditor instance should correctly load the last hash.")

    def test_get_last_log_hash_empty_or_no_file(self):
        # No file exists yet
        self.assertIsNone(self.auditor.last_log_hash, "Should be None if no log file yet.")

        # Create an empty file
        self.auditor.audit_log_file.touch()
        auditor_empty_file = DataTransformationAuditor(log_dir_path=str(self.test_dir))
        self.assertIsNone(auditor_empty_file.last_log_hash, "Should be None for an empty log file.")

        # Create a file with malformed JSON
        with open(self.auditor.audit_log_file, 'w') as f:
            f.write("this is not json\n")
        auditor_bad_file = DataTransformationAuditor(log_dir_path=str(self.test_dir))
        self.assertIsNone(auditor_bad_file.last_log_hash, "Should be None for malformed log file.")


if __name__ == '__main__':
    unittest.main()
