import json
import hashlib
import datetime

class DataTransformationAuditor:
    """
    Audits data classification and obfuscation events, creating a tamper-evident log.
    """
    def __init__(self, log_file_path: str = "_data/audit_log.jsonl"):
        self.log_file_path = log_file_path
        self.last_log_hash = self._get_last_log_hash()

    def _get_last_log_hash(self) -> str:
        """Retrieves the hash of the last entry in the log file."""
        try:
            with open(self.log_file_path, "rb") as f:
                last_line = f.readlines()[-1]
                return json.loads(last_line)["log_hash"]
        except (IOError, IndexError):
            return ""

    def log_event(self, event_type: str, original_data: dict, transformed_data: dict, policy_id: str, consent_id: str, outcome: str):
        """Logs a data transformation event."""
        timestamp = datetime.datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "original_data_hash": hashlib.sha256(json.dumps(original_data, sort_keys=True).encode()).hexdigest(),
            "transformed_data_hash": hashlib.sha256(json.dumps(transformed_data, sort_keys=True).encode()).hexdigest(),
            "policy_id": policy_id,
            "consent_id": consent_id,
            "outcome": outcome,
            "previous_log_hash": self.last_log_hash
        }

        log_hash = hashlib.sha256(json.dumps(log_entry, sort_keys=True).encode()).hexdigest()
        log_entry_with_hash = {**log_entry, "log_hash": log_hash}

        with open(self.log_file_path, "a") as f:
            f.write(json.dumps(log_entry_with_hash) + "\n")

        self.last_log_hash = log_hash
