import unittest
import json
from privacy_protocol_core.consent import UserConsent
from privacy_protocol_core.policy import DataCategory, Purpose # For enum values

class TestUserConsent(unittest.TestCase):

    def test_consent_instantiation_defaults(self):
        consent = UserConsent(user_id="user1", policy_id="policy1")
        self.assertIsNotNone(consent.consent_id)
        self.assertEqual(consent.user_id, "user1")
        self.assertEqual(consent.policy_id, "policy1")
        self.assertIsNone(consent.policy_version)
        self.assertEqual(consent.data_categories_consented, [])
        self.assertEqual(consent.purposes_consented, [])
        self.assertEqual(consent.third_parties_consented, [])
        self.assertIsNotNone(consent.timestamp)
        self.assertTrue(consent.is_active)
        self.assertIsNone(consent.signature)
        self.assertIsNone(consent.consent_source)
        self.assertIsNone(consent.expires_at)

    def test_consent_instantiation_with_values(self):
        dc = [DataCategory.PERSONAL_INFO, DataCategory.LOCATION_DATA]
        p = [Purpose.SERVICE_DELIVERY, Purpose.MARKETING]
        consent = UserConsent(
            consent_id="test_consent_id",
            user_id="user2",
            policy_id="policy2",
            policy_version="1.1",
            data_categories_consented=dc,
            purposes_consented=p,
            third_parties_consented=["AdNetwork A"],
            is_active=False,
            signature="dummy_sig",
            consent_source="app_v1",
            expires_at="2025-12-31T23:59:59Z"
        )
        self.assertEqual(consent.consent_id, "test_consent_id")
        self.assertEqual(consent.user_id, "user2")
        self.assertEqual(consent.policy_id, "policy2")
        self.assertEqual(consent.policy_version, "1.1")
        self.assertEqual(consent.data_categories_consented, dc)
        self.assertEqual(consent.purposes_consented, p)
        self.assertEqual(consent.third_parties_consented, ["AdNetwork A"])
        self.assertFalse(consent.is_active)
        self.assertEqual(consent.signature, "dummy_sig")
        self.assertEqual(consent.consent_source, "app_v1")
        self.assertEqual(consent.expires_at, "2025-12-31T23:59:59Z")

    def test_to_dict(self):
        dc = [DataCategory.USAGE_DATA]
        p = [Purpose.ANALYTICS]
        consent = UserConsent(user_id="user3", policy_id="policy3", data_categories_consented=dc, purposes_consented=p)
        consent_dict = consent.to_dict()

        self.assertEqual(consent_dict["consent_id"], consent.consent_id)
        self.assertEqual(consent_dict["user_id"], "user3")
        self.assertEqual(consent_dict["policy_id"], "policy3")
        self.assertEqual(consent_dict["data_categories_consented"], [d.value for d in dc])
        self.assertEqual(consent_dict["purposes_consented"], [ps.value for ps in p])
        self.assertTrue(consent_dict["is_active"])

    def test_to_json(self):
        consent = UserConsent(user_id="user4", policy_id="policy4", consent_source="test_json")
        consent_json = consent.to_json()
        consent_data_from_json = json.loads(consent_json)

        self.assertEqual(consent_data_from_json["consent_id"], consent.consent_id)
        self.assertEqual(consent_data_from_json["consent_source"], "test_json")

    def test_from_dict(self):
        consent_data = {
            "consent_id": "dict_consent_id",
            "user_id": "user5",
            "policy_id": "policy5",
            "policy_version": "2.0",
            "data_categories_consented": [DataCategory.BIOMETRIC_DATA.value, "InvalidCategory"],
            "purposes_consented": [Purpose.SECURITY.value],
            "third_parties_consented": ["SecurityPartner X"],
            "is_active": False,
            "consent_source": "dict_load"
        }
        consent = UserConsent.from_dict(consent_data)

        self.assertEqual(consent.consent_id, "dict_consent_id")
        self.assertEqual(consent.user_id, "user5")
        self.assertEqual(consent.policy_version, "2.0")
        self.assertEqual(len(consent.data_categories_consented), 1)
        self.assertIn(DataCategory.BIOMETRIC_DATA, consent.data_categories_consented)
        self.assertNotIn("InvalidCategory", [dc.value for dc in consent.data_categories_consented])
        self.assertIn(Purpose.SECURITY, consent.purposes_consented)
        self.assertEqual(consent.third_parties_consented, ["SecurityPartner X"])
        self.assertFalse(consent.is_active)
        self.assertEqual(consent.consent_source, "dict_load")

    def test_from_json(self):
        consent_data = {
            "consent_id": "json_consent_id",
            "user_id": "user6",
            "policy_id": "policy6",
            "purposes_consented": [Purpose.PERSONALIZATION.value, "InvalidPurpose"]
        }
        consent_json = json.dumps(consent_data)
        consent = UserConsent.from_json(consent_json)

        self.assertEqual(consent.consent_id, "json_consent_id")
        self.assertEqual(consent.user_id, "user6")
        self.assertEqual(len(consent.purposes_consented), 1)
        self.assertIn(Purpose.PERSONALIZATION, consent.purposes_consented)

    def test_revoke(self):
        consent = UserConsent(user_id="user7", policy_id="policy7", is_active=True)
        self.assertTrue(consent.is_active)
        consent.revoke()
        self.assertFalse(consent.is_active)

    def test_repr(self):
        consent = UserConsent(consent_id="repr_consent", user_id="user_repr", policy_id="policy_repr", is_active=True)
        self.assertEqual(repr(consent), "<UserConsent(consent_id='repr_consent', user_id='user_repr', policy_id='policy_repr', active=True)>")

if __name__ == '__main__':
    unittest.main()
