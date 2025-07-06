# Placeholder for logging metadata about content origins and interactions
import datetime

class MetadataLogger:
    def __init__(self):
        self.log_entries = []

    def log_interaction(self, user_id, policy_url, action, details=None):
        """Logs an interaction with a privacy policy."""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "policy_url": policy_url,
            "action": action, # e.g., "viewed", "risk_assessed", "opt_out_clicked"
            "details": details if details else {}
        }
        self.log_entries.append(entry)

    def get_logs_for_user(self, user_id):
        """Retrieves all logs for a specific user."""
        return [entry for entry in self.log_entries if entry["user_id"] == user_id]
