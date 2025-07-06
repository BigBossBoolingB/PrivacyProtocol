import unittest
import time
from privacy_protocol_core.data_tracking.policy_tracker import PolicyTracker

class TestPolicyTracker(unittest.TestCase):

    def setUp(self):
        self.tracker = PolicyTracker()
        self.test_url = "http://example.com/privacy"

    def test_add_policy_version(self):
        ts1 = time.time()
        self.tracker.add_policy_version(self.test_url, "Version 1 text", ts1)
        self.assertIn(self.test_url, self.tracker.policy_history)
        self.assertEqual(len(self.tracker.policy_history[self.test_url]), 1)
        self.assertEqual(self.tracker.policy_history[self.test_url][0]["version"], 1)
        self.assertEqual(self.tracker.policy_history[self.test_url][0]["text"], "Version 1 text")
        self.assertEqual(self.tracker.policy_history[self.test_url][0]["timestamp"], ts1)

        ts2 = time.time()
        self.tracker.add_policy_version(self.test_url, "Version 2 text - updated", ts2)
        self.assertEqual(len(self.tracker.policy_history[self.test_url]), 2)
        self.assertEqual(self.tracker.policy_history[self.test_url][1]["version"], 2)
        self.assertEqual(self.tracker.policy_history[self.test_url][1]["text"], "Version 2 text - updated")

    def test_get_policy_changes_no_history(self):
        changes = self.tracker.get_policy_changes("http://nonexistent.com/privacy")
        self.assertEqual(changes, "No changes or insufficient history.")

    def test_get_policy_changes_one_version(self):
        self.tracker.add_policy_version(self.test_url, "Version 1 text", time.time())
        changes = self.tracker.get_policy_changes(self.test_url)
        self.assertEqual(changes, "No changes or insufficient history.")

    def test_get_policy_changes_with_multiple_versions(self):
        self.tracker.add_policy_version(self.test_url, "Version 1 text", time.time())
        time.sleep(0.01) # Ensure timestamp is different
        self.tracker.add_policy_version(self.test_url, "Version 2 text - updated", time.time())

        # Current placeholder returns a generic message
        expected_message = "Changes detected (details to be implemented)."
        changes = self.tracker.get_policy_changes(self.test_url)
        self.assertEqual(changes, expected_message)

    # TODO: Add tests for actual diffing logic once implemented.
    # For example, provide two texts and assert the specific differences found.

if __name__ == '__main__':
    unittest.main()
