# src/privacy_framework/data_auditor.py
"""
Audits data transformation events for logging and tamper evidence.
"""
import json
import hashlib
import time
import os
from typing import Dict, Any, Optional

class DataTransformationAuditor:
    """
    Logs data classification, evaluation, and obfuscation events.
    Creates a tamper-evident log by chaining hashes of log entries.
    """

    def __init__(self, audit_log_filepath: str = "_app_data/audit_log.jsonl"):
        """
        Initializes the DataTransformationAuditor.

        Args:
            audit_log_filepath (str): Path to the audit log file.
        """
        self.audit_log_filepath = audit_log_filepath
        self.last_log_hash: Optional[str] = None

        # Ensure the directory for the audit log exists
        log_dir = os.path.dirname(self.audit_log_filepath)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError as e:
                print(f"Error creating audit log directory {log_dir}: {e}")
                # Depending on desired robustness, could raise error or operate without logging.
                # For now, it will fail when trying to write.

        # TODO: In a production system, consider log rotation, secure storage,
        #       and integration with dedicated logging/auditing systems or blockchain.
        #       For EmPower1 Blockchain integration, log entries (or their batched hashes)
        #       could be recorded as transactions.

        # Initialize last_log_hash from existing log file if any
        self._initialize_last_hash()

    def _calculate_data_hash(self, data: Any) -> Optional[str]:
        """Calculates SHA256 hash of any JSON-serializable data."""
        if data is None:
            return None
        try:
            # Sort keys for consistent hashing of dictionaries
            serialized_data = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
            return hashlib.sha256(serialized_data).hexdigest()
        except TypeError: # Not JSON serializable
            return hashlib.sha256(str(data).encode('utf-8')).hexdigest()


    def _calculate_log_entry_hash(self, entry_data: Dict[str, Any]) -> str:
        """Calculates SHA256 hash of a log entry dictionary (excluding previous_hash for chaining)."""
        # Ensure consistent hashing by sorting keys
        # We hash the entry *before* adding the 'current_entry_hash' to avoid recursion.
        # The 'previous_log_hash' is part of the data being hashed for the current entry's hash.
        serialized_entry = json.dumps(entry_data, sort_keys=True, separators=(',', ':')).encode('utf-8')
        return hashlib.sha256(serialized_entry).hexdigest()

    def _initialize_last_hash(self):
        """Reads the last entry of the log file to set the initial last_log_hash."""
        if not os.path.exists(self.audit_log_filepath):
            return # No log file, so no previous hash

        last_line = None
        try:
            with open(self.audit_log_filepath, 'rb') as f: # Read in binary for seek
                try:  # catch OSError in case of a zero byte file
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, os.SEEK_CUR)
                except OSError:
                    f.seek(0)
                last_line_bytes = f.readline()
                if last_line_bytes:
                    last_line = last_line_bytes.decode('utf-8')

            if last_line:
                last_log_entry = json.loads(last_line)
                self.last_log_hash = last_log_entry.get("current_entry_hash")
        except (IOError, json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not initialize last_log_hash from {self.audit_log_filepath}: {e}")
            # Potentially mark log as possibly tampered or start a new chain.
            self.last_log_hash = None # Treat as if no valid previous log.


    def log_event(self,
                  event_type: str,
                  details: Dict[str, Any],
                  original_data: Optional[Any] = None,
                  processed_data: Optional[Any] = None,
                  policy_id: Optional[str] = None,
                  consent_id: Optional[str] = None
                  ) -> None:
        """
        Logs a data transformation or access event.

        Args:
            event_type (str): Type of event (e.g., "DATA_CLASSIFICATION", "OBFUSCATION_APPLIED",
                                            "ACCESS_PERMITTED_RAW", "ACCESS_DENIED").
            details (Dict[str, Any]): A dictionary of event-specific details.
            original_data (Optional[Any]): The original data (or relevant parts).
            processed_data (Optional[Any]): The data after processing/obfuscation.
            policy_id (Optional[str]): ID of the policy applied.
            consent_id (Optional[str]): ID of the consent record applied.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime(time.time())) # ISO 8601 format with milliseconds

        log_entry_data_to_hash = {
            "timestamp": timestamp,
            "event_type": event_type,
            "previous_log_hash": self.last_log_hash, # Link to previous entry
            "details": details,
            "policy_id": policy_id,
            "consent_id": consent_id,
            "original_data_hash": self._calculate_data_hash(original_data) if original_data is not None else None,
            "processed_data_hash": self._calculate_data_hash(processed_data) if processed_data is not None else None,
        }

        current_entry_hash = self._calculate_log_entry_hash(log_entry_data_to_hash)

        full_log_entry = {
            **log_entry_data_to_hash,
            "current_entry_hash": current_entry_hash # Add the hash of this entry
        }

        try:
            with open(self.audit_log_filepath, 'a') as f: # Append mode
                json.dump(full_log_entry, f)
                f.write('\n') # Newline for JSON Lines format
            self.last_log_hash = current_entry_hash # Update for next entry
        except IOError as e:
            print(f"Error writing to audit log {self.audit_log_filepath}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while writing audit log: {e}")


if __name__ == '__main__':
    # Example Usage
    audit_log_file = "_app_data_demo/audit_log_test.jsonl"
    if os.path.exists(audit_log_file):
        os.remove(audit_log_file) # Clean start for demo

    auditor = DataTransformationAuditor(audit_log_filepath=audit_log_file)

    print(f"Initial last_log_hash: {auditor.last_log_hash}")

    sample_original_data1 = {"email": "test1@example.com", "ip": "1.1.1.1"}
    sample_processed_data1 = {"email": "[REDACTED]", "ip": "[REDACTED]"}
    auditor.log_event(
        event_type="DATA_OBFUSCATED",
        details={"reason": "Marketing consent denied", "fields_obfuscated": ["email", "ip"]},
        original_data=sample_original_data1,
        processed_data=sample_processed_data1,
        policy_id="policy123",
        consent_id="consentABC"
    )
    print(f"Logged event 1. New last_log_hash: {auditor.last_log_hash}")

    sample_original_data2 = {"user_id": "user456", "action": "login"}
    auditor.log_event(
        event_type="ACCESS_PERMITTED_RAW",
        details={"message": "Login attempt, raw access permitted by policy."},
        original_data=sample_original_data2,
        processed_data=sample_original_data2, # Same as original
        policy_id="policy789",
        consent_id=None # No specific consent needed, e.g., legitimate interest
    )
    print(f"Logged event 2. New last_log_hash: {auditor.last_log_hash}")

    print(f"\nAudit log content ({audit_log_file}):")
    if os.path.exists(audit_log_file):
        with open(audit_log_file, 'r') as f:
            for line in f:
                print(line.strip())

    # Simulate re-initialization to check hash chaining
    print("\nSimulating auditor restart...")
    auditor_restarted = DataTransformationAuditor(audit_log_filepath=audit_log_file)
    print(f"Restarted auditor's last_log_hash: {auditor_restarted.last_log_hash} (should match last event's hash)")
    assert auditor_restarted.last_log_hash == auditor.last_log_hash

    sample_original_data3 = {"query": "sensitive search"}
    auditor_restarted.log_event(
        event_type="DATA_CLASSIFIED",
        details={"classification": "HIGH_SENSITIVITY_SEARCH_TERM"},
        original_data=sample_original_data3,
        policy_id="policy_search_terms"
    )
    print(f"Logged event 3 (after restart). New last_log_hash: {auditor_restarted.last_log_hash}")
    assert auditor_restarted.last_log_hash != auditor.last_log_hash # Hash should have changed

    # Clean up
    # if os.path.exists("_app_data_demo"):
    #     shutil.rmtree("_app_data_demo")
    #     print("\nCleaned up _app_data_demo.")
