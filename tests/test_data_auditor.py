# tests/test_data_auditor.py
import unittest
import os
import shutil
import json
import hashlib

# Adjust import path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.privacy_framework.data_auditor import DataTransformationAuditor

class TestDataTransformationAuditor(unittest.TestCase):
    TEST_AUDIT_LOG_DIR = "_app_data_test/audit_logs/"
    TEST_AUDIT_LOG_FILE = os.path.join(TEST_AUDIT_LOG_DIR, "test_audit.jsonl")

    def setUp(self):
        """Set up a clean audit log directory for each test."""
        if os.path.exists(self.TEST_AUDIT_LOG_DIR):
            shutil.rmtree(self.TEST_AUDIT_LOG_DIR)
        # Auditor will create the directory if it doesn't exist upon first write.
        # For _initialize_last_hash, we might need it to exist or handle gracefully.
        # The DataTransformationAuditor's __init__ handles directory creation.
        self.auditor = DataTransformationAuditor(audit_log_filepath=self.TEST_AUDIT_LOG_FILE)

    def tearDown(self):
        """Clean up the audit log directory after each test."""
        if os.path.exists(self.TEST_AUDIT_LOG_DIR):
            shutil.rmtree(self.TEST_AUDIT_LOG_DIR)

    def _read_log_entries(self) -> list:
        entries = []
        if os.path.exists(self.TEST_AUDIT_LOG_FILE):
            with open(self.TEST_AUDIT_LOG_FILE, 'r') as f:
                for line in f:
                    entries.append(json.loads(line))
        return entries

    def test_log_directory_creation(self):
        log_dir = os.path.dirname(self.TEST_AUDIT_LOG_FILE)
        # setUp already creates an auditor instance, which should create the dir.
        self.assertTrue(os.path.exists(log_dir))

    def test_log_event_creates_file_and_entry(self):
        self.assertFalse(os.path.exists(self.TEST_AUDIT_LOG_FILE))
        self.auditor.log_event(
            event_type="TEST_EVENT",
            details={"message": "This is a test event"},
            policy_id="p1", consent_id="c1"
        )
        self.assertTrue(os.path.exists(self.TEST_AUDIT_LOG_FILE))
        entries = self._read_log_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["event_type"], "TEST_EVENT")
        self.assertEqual(entries[0]["details"]["message"], "This is a test event")
        self.assertIsNotNone(entries[0]["timestamp"])
        self.assertIsNone(entries[0]["previous_log_hash"]) # First entry
        self.assertIsNotNone(entries[0]["current_entry_hash"])

    def test_log_chaining(self):
        self.auditor.log_event("EVENT_1", {"data": "first"}, "p1")
        entries1 = self._read_log_entries()
        hash1 = entries1[0]["current_entry_hash"]
        self.assertEqual(self.auditor.last_log_hash, hash1)

        self.auditor.log_event("EVENT_2", {"data": "second"}, "p2")
        entries2 = self._read_log_entries()
        self.assertEqual(len(entries2), 2)
        self.assertEqual(entries2[1]["previous_log_hash"], hash1)
        hash2 = entries2[1]["current_entry_hash"]
        self.assertEqual(self.auditor.last_log_hash, hash2)
        self.assertNotEqual(hash1, hash2)

    def test_calculate_data_hash_consistency(self):
        data1 = {"key1": "value1", "key2": 123}
        data2 = {"key2": 123, "key1": "value1"} # Same data, different order
        hash1 = self.auditor._calculate_data_hash(data1)
        hash2 = self.auditor._calculate_data_hash(data2)
        self.assertEqual(hash1, hash2)

        data3 = {"key1": "value1", "key2": "123"} # Different type for value
        hash3 = self.auditor._calculate_data_hash(data3)
        self.assertNotEqual(hash1, hash3)

        self.assertIsNone(self.auditor._calculate_data_hash(None))

        # Test non-JSON serializable (falls back to str hash)
        class NonSerializable: pass
        non_serializable_obj = NonSerializable()
        hash_non_serial = self.auditor._calculate_data_hash(non_serializable_obj)
        self.assertIsNotNone(hash_non_serial)
        # Hash of its string representation
        expected_str_hash = hashlib.sha256(str(non_serializable_obj).encode('utf-8')).hexdigest()
        self.assertEqual(hash_non_serial, expected_str_hash)


    def test_initialize_last_hash_from_existing_log(self):
        # Manually create a log file with one entry
        entry1_data_to_hash = {
            "timestamp": "ts1", "event_type": "PRE_EXISTING_EVENT",
            "previous_log_hash": None, "details": {}, "policy_id": "p0",
            "original_data_hash": None, "processed_data_hash": None
        }
        entry1_hash = self.auditor._calculate_log_entry_hash(entry1_data_to_hash)
        full_entry1 = {**entry1_data_to_hash, "current_entry_hash": entry1_hash}

        os.makedirs(os.path.dirname(self.TEST_AUDIT_LOG_FILE), exist_ok=True)
        with open(self.TEST_AUDIT_LOG_FILE, 'w') as f:
            json.dump(full_entry1, f)
            f.write('\n')

        # Create a new auditor instance, it should pick up the hash
        new_auditor = DataTransformationAuditor(audit_log_filepath=self.TEST_AUDIT_LOG_FILE)
        self.assertEqual(new_auditor.last_log_hash, entry1_hash)

        # Log another event with this new auditor
        new_auditor.log_event("EVENT_AFTER_RESTART", {"data": "new data"}, "p_new")
        entries = self._read_log_entries()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1]["previous_log_hash"], entry1_hash)
        self.assertNotEqual(entries[1]["current_entry_hash"], entry1_hash)


    def test_initialize_last_hash_empty_file(self):
        # Create an empty log file
        os.makedirs(os.path.dirname(self.TEST_AUDIT_LOG_FILE), exist_ok=True)
        open(self.TEST_AUDIT_LOG_FILE, 'w').close()

        new_auditor = DataTransformationAuditor(audit_log_filepath=self.TEST_AUDIT_LOG_FILE)
        self.assertIsNone(new_auditor.last_log_hash)

    def test_initialize_last_hash_corrupted_file(self):
        # Create a corrupted (not JSON) log file
        os.makedirs(os.path.dirname(self.TEST_AUDIT_LOG_FILE), exist_ok=True)
        with open(self.TEST_AUDIT_LOG_FILE, 'w') as f:
            f.write("this is not json\n")

        # Suppress print for this test as error is expected
        with unittest.mock.patch('builtins.print') as mock_print:
            new_auditor = DataTransformationAuditor(audit_log_filepath=self.TEST_AUDIT_LOG_FILE)
            self.assertIsNone(new_auditor.last_log_hash)
            mock_print.assert_called() # Check that a warning was printed

if __name__ == '__main__':
    unittest.main()
