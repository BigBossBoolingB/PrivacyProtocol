import unittest
import json
from privacy_protocol_core.policy import PrivacyPolicy, DataCategory, Purpose, LegalBasis

class TestPrivacyPolicy(unittest.TestCase):

    def test_policy_instantiation_defaults(self):
        policy = PrivacyPolicy()
        self.assertIsNotNone(policy.policy_id)
        self.assertEqual(policy.version, "1.0")
        self.assertEqual(policy.data_categories, [])
        self.assertEqual(policy.purposes, [])
        self.assertEqual(policy.retention_period, "Not Specified")
        self.assertEqual(policy.third_parties_shared_with, [])
        self.assertEqual(policy.legal_basis, [])
        self.assertEqual(policy.text_summary, "")
        self.assertIsNotNone(policy.last_updated)
        self.assertIsNotNone(policy.created_at)

    def test_policy_instantiation_with_values(self):
        dc = [DataCategory.PERSONAL_INFO, DataCategory.USAGE_DATA]
        p = [Purpose.SERVICE_DELIVERY, Purpose.ANALYTICS]
        lb = [LegalBasis.CONSENT, LegalBasis.CONTRACT]
        policy = PrivacyPolicy(
            policy_id="test_id_123",
            version="2.0",
            data_categories=dc,
            purposes=p,
            retention_period="30 days",
            third_parties_shared_with=["Partner A", "Partner B"],
            legal_basis=lb,
            text_summary="A test policy."
        )
        self.assertEqual(policy.policy_id, "test_id_123")
        self.assertEqual(policy.version, "2.0")
        self.assertEqual(policy.data_categories, dc)
        self.assertEqual(policy.purposes, p)
        self.assertEqual(policy.retention_period, "30 days")
        self.assertEqual(policy.third_parties_shared_with, ["Partner A", "Partner B"])
        self.assertEqual(policy.legal_basis, lb)
        self.assertEqual(policy.text_summary, "A test policy.")

    def test_to_dict(self):
        dc = [DataCategory.LOCATION_DATA]
        p = [Purpose.MARKETING]
        lb = [LegalBasis.LEGITIMATE_INTERESTS]
        policy = PrivacyPolicy(data_categories=dc, purposes=p, legal_basis=lb, text_summary="dict test")
        policy_dict = policy.to_dict()

        self.assertEqual(policy_dict["policy_id"], policy.policy_id)
        self.assertEqual(policy_dict["version"], policy.version)
        self.assertEqual(policy_dict["data_categories"], [d.value for d in dc])
        self.assertEqual(policy_dict["purposes"], [ps.value for ps in p])
        self.assertEqual(policy_dict["legal_basis"], [lbs.value for lbs in lb])
        self.assertEqual(policy_dict["text_summary"], "dict test")
        self.assertIn("last_updated", policy_dict)
        self.assertIn("created_at", policy_dict)

    def test_to_json(self):
        policy = PrivacyPolicy(text_summary="json test")
        policy_json = policy.to_json()
        policy_data_from_json = json.loads(policy_json)

        self.assertEqual(policy_data_from_json["policy_id"], policy.policy_id)
        self.assertEqual(policy_data_from_json["text_summary"], "json test")

    def test_from_dict(self):
        policy_data = {
            "policy_id": "dict_policy_id",
            "version": "1.5",
            "data_categories": [DataCategory.FINANCIAL_INFO.value, "InvalidCategory"],
            "purposes": [Purpose.SECURITY.value],
            "retention_period": "1 year",
            "third_parties_shared_with": ["Bank C"],
            "legal_basis": [LegalBasis.LEGAL_OBLIGATION.value, "InvalidBasis"],
            "text_summary": "Loaded from dict.",
            "last_updated": "2023-01-01T00:00:00Z",
            "created_at": "2022-01-01T00:00:00Z" # This won't be used by from_dict, set at instantiation
        }
        policy = PrivacyPolicy.from_dict(policy_data)

        self.assertEqual(policy.policy_id, "dict_policy_id")
        self.assertEqual(policy.version, "1.5")
        self.assertEqual(len(policy.data_categories), 1)
        self.assertIn(DataCategory.FINANCIAL_INFO, policy.data_categories)
        self.assertNotIn("InvalidCategory", [dc.value for dc in policy.data_categories])
        self.assertEqual(len(policy.purposes), 1)
        self.assertIn(Purpose.SECURITY, policy.purposes)
        self.assertEqual(policy.retention_period, "1 year")
        self.assertEqual(policy.third_parties_shared_with, ["Bank C"])
        self.assertEqual(len(policy.legal_basis), 1)
        self.assertIn(LegalBasis.LEGAL_OBLIGATION, policy.legal_basis)
        self.assertEqual(policy.text_summary, "Loaded from dict.")
        self.assertEqual(policy.last_updated, "2023-01-01T00:00:00Z")

    def test_from_json(self):
        policy_data = {
            "policy_id": "json_policy_id",
            "version": "1.8",
            "data_categories": [DataCategory.HEALTH_INFO.value],
            "purposes": [Purpose.RESEARCH_DEVELOPMENT.value],
            "text_summary": "Loaded from json."
        }
        policy_json = json.dumps(policy_data)
        policy = PrivacyPolicy.from_json(policy_json)

        self.assertEqual(policy.policy_id, "json_policy_id")
        self.assertEqual(policy.version, "1.8")
        self.assertIn(DataCategory.HEALTH_INFO, policy.data_categories)
        self.assertIn(Purpose.RESEARCH_DEVELOPMENT, policy.purposes)
        self.assertEqual(policy.text_summary, "Loaded from json.")

    def test_repr(self):
        policy = PrivacyPolicy(policy_id="repr_id", version="3.0")
        self.assertEqual(repr(policy), "<PrivacyPolicy(policy_id='repr_id', version='3.0')>")

if __name__ == '__main__':
    unittest.main()
