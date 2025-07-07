import json
import os
import hashlib
import uuid # Added missing import
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

class DataTransformationAuditor:
    def __init__(self, log_dir_path: str = "./_app_data/audit_logs/"):
        self.log_dir_path = Path(log_dir_path)
        self._ensure_dir_exists(self.log_dir_path)
        self.audit_log_file = self.log_dir_path / "transformation_audit.jsonl"
        self.last_log_hash: Optional[str] = self._get_last_log_hash()

    def _ensure_dir_exists(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

    def _get_last_log_hash(self) -> Optional[str]:
        """Reads the last line of the log file to get its hash, if available."""
        if not self.audit_log_file.exists():
            return None
        try:
            with open(self.audit_log_file, 'rb') as f:
                # Go to the end of the file to find the last line efficiently
                try:  # catch OSError in case of empty file...
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, os.SEEK_CUR)
                except OSError: # ...or if the file is too short.
                    f.seek(0)

                last_line_str = f.readline().decode('utf-8')
                if not last_line_str: # Empty file or only one line without newline
                    f.seek(0)
                    last_line_str = f.read().decode('utf-8').strip()
                    if not last_line_str: return None


            last_log_entry = json.loads(last_line_str)
            # The hash of the log entry *itself* is what we'd use for chaining.
            # For simplicity here, we'll just use a dedicated 'entry_hash' field if present.
            # A more robust chain would hash the canonical JSON string of the *previous* entry.
            # The plan was to include hash of *previous* log entry.
            # So, the 'entry_hash' of the last log *is* the hash of that entry.
            # What we need for a new entry is the hash of the *last written entry*.

            # Let's define that each entry will have its own hash.
            # The `previous_log_hash` will be the hash of the entry before it.
            # The last_log_hash should be the current_entry_hash of the last entry.
            parsed_entry = json.loads(last_line_str)
            return parsed_entry.get("current_entry_hash")

        except (IOError, json.JSONDecodeError, IndexError, AttributeError): # Added AttributeError for .get
            # print(f"Debug: Could not read or parse last log hash from {self.audit_log_file}")
            return None # If file is empty, malformed, or doesn't exist

    def _hash_log_entry_content(self, entry_string: str) -> str:
        """Hashes the string content of a log entry."""
        return hashlib.sha256(entry_string.encode('utf-8')).hexdigest()

    def log_event(self,
                  event_type: str,
                  user_id: str,
                  policy_id: str,
                  policy_version: str,
                  consent_id: Optional[str],
                  input_data_hash: str,
                  output_data_hash: Optional[str],
                  transformation_details: Dict[str, Any],
                  status: str,
                  timestamp: Optional[str] = None) -> bool:
        """
        Logs a data transformation or access event.

        Args:
            event_type: Type of event (e.g., "DATA_ACCESS_RAW", "DATA_OBFUSCATED").
            user_id: ID of the user whose data is processed.
            policy_id: ID of the policy applied.
            policy_version: Version of the policy applied.
            consent_id: ID of the consent record applied, if any.
            input_data_hash: SHA256 hash of the canonical representation of input data.
            output_data_hash: SHA256 hash of the canonical representation of output data (if different or transformed).
            transformation_details: Dict describing what transformations occurred (e.g., fields affected, methods).
            status: Final status of the operation (e.g., "Allowed_Raw", "Allowed_Transformed").
            timestamp: ISO format timestamp of the event. Defaults to now if None.

        Returns:
            True if logging was successful, False otherwise.
        """
        log_entry: Dict[str, Any] = {
            "event_id": str(uuid.uuid4()),
            "timestamp": timestamp if timestamp else datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "policy_id": policy_id,
            "policy_version": policy_version,
            "consent_id": consent_id,
            "input_data_hash": input_data_hash,
            "output_data_hash": output_data_hash,
            "transformation_details": transformation_details,
            "status": status,
            "previous_log_hash": self.last_log_hash # Link to the previous log entry
        }

        try:
            # Create a canonical string representation for hashing the current entry
            # Ensure keys are sorted for consistent hashing if dict is not ordered (Python 3.7+)
            log_entry_str = json.dumps(log_entry, sort_keys=True)
            current_entry_hash = self._hash_log_entry_content(log_entry_str)
            log_entry["current_entry_hash"] = current_entry_hash # Add hash of this entry itself

            with open(self.audit_log_file, 'a') as f:
                # Re-serialize with the new hash for writing, ensure consistent order
                f.write(json.dumps(log_entry, sort_keys=True) + "\n")

            self.last_log_hash = current_entry_hash # Update for the next log event
            return True
        except IOError as e:
            print(f"Error writing to audit log {self.audit_log_file}: {e}")
            return False
        except Exception as e: # Catch other potential errors like TypeError during json.dumps
            print(f"An unexpected error occurred during audit logging: {e}")
            return False

    @staticmethod
    def hash_data(data: Dict[str, Any]) -> str:
        """
        Creates a SHA256 hash of a dictionary by serializing it to a canonical JSON string.
        """
        # Sort keys to ensure canonical representation
        canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()


if __name__ == '__main__':
    import tempfile
    import shutil
    import uuid # Ensure uuid is imported for the main block if not at top level

    temp_audit_dir = tempfile.mkdtemp()
    print(f"Using temporary directory for DataTransformationAuditor: {temp_audit_dir}")
    auditor = DataTransformationAuditor(log_dir_path=temp_audit_dir)

    sample_input1 = {"email": "test@example.com", "ip": "1.2.3.4"}
    sample_output1_raw = {"email": "test@example.com", "ip": "1.2.3.4"}

    sample_input2 = {"credit_card": "1234-5678-9012-3456"}
    sample_output2_obfuscated = {"credit_card": "[REDACTED]"}

    input1_hash = DataTransformationAuditor.hash_data(sample_input1)
    output1_hash = DataTransformationAuditor.hash_data(sample_output1_raw)

    input2_hash = DataTransformationAuditor.hash_data(sample_input2)
    output2_hash = DataTransformationAuditor.hash_data(sample_output2_obfuscated)

    print("\n--- Logging First Event ---")
    success1 = auditor.log_event(
        event_type="DATA_ACCESS_RAW",
        user_id="user123",
        policy_id="policy_xyz",
        policy_version="1.1",
        consent_id="consent_abc",
        input_data_hash=input1_hash,
        output_data_hash=output1_hash, # Same as input for raw access
        transformation_details={"fields_accessed_raw": ["email", "ip"]},
        status="Allowed_Raw"
    )
    print(f"Log event 1 success: {success1}, Last log hash: {auditor.last_log_hash}")
    assert success1
    assert auditor.last_log_hash is not None
    first_event_hash = auditor.last_log_hash

    print("\n--- Logging Second Event ---")
    success2 = auditor.log_event(
        event_type="DATA_OBFUSCATED",
        user_id="user456",
        policy_id="policy_xyz",
        policy_version="1.1",
        consent_id="consent_def",
        input_data_hash=input2_hash,
        output_data_hash=output2_hash,
        transformation_details={"fields_obfuscated": {"credit_card": "REDACT"}},
        status="Allowed_Transformed"
    )
    print(f"Log event 2 success: {success2}, Last log hash: {auditor.last_log_hash}")
    assert success2
    assert auditor.last_log_hash is not None
    assert auditor.last_log_hash != first_event_hash # Hash should change
    second_event_hash = auditor.last_log_hash

    print("\n--- Verifying Log File Content (first few lines) ---")
    if auditor.audit_log_file.exists():
        with open(auditor.audit_log_file, 'r') as f:
            lines = f.readlines()
            print(f"Total lines in log: {len(lines)}")
            for i, line_str in enumerate(lines[:5]): # Print first 5 lines
                print(f"Line {i+1}: {line_str.strip()}")
                entry = json.loads(line_str)
                if i == 0:
                    assert entry["previous_log_hash"] is None
                    assert entry["current_entry_hash"] == first_event_hash
                if i == 1:
                    assert entry["previous_log_hash"] == first_event_hash
                    assert entry["current_entry_hash"] == second_event_hash
            assert len(lines) == 2
    else:
        print("Audit log file not found!")

    # Test _get_last_log_hash on existing file
    auditor_reloaded = DataTransformationAuditor(log_dir_path=temp_audit_dir)
    print(f"\nReloaded auditor, last log hash should be of second event: {auditor_reloaded.last_log_hash}")
    assert auditor_reloaded.last_log_hash == second_event_hash


    # Clean up
    try:
        shutil.rmtree(temp_audit_dir)
        print(f"\nCleaned up temporary directory: {temp_audit_dir}")
    except Exception as e:
        print(f"Error cleaning up temp directory {temp_audit_dir}: {e}")

    print("\nDataTransformationAuditor examples finished.")
