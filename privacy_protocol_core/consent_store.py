import json
import os
import glob
from pathlib import Path
import re
from typing import Optional, List
from datetime import datetime, timezone # Ensure timezone is available

try:
    from .consent import UserConsent
except ImportError: # For standalone testing
    from consent import UserConsent

class ConsentStore:
    def __init__(self, base_path: str = "./_data/consents/"):
        self.base_path = Path(base_path)
        # No top-level _ensure_dir_exists here, as user/policy subdirs are made on demand

    def _ensure_dir_exists(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

    def _get_consent_dir_path(self, user_id: str, policy_id: str) -> Path:
        # Sanitize user_id and policy_id for directory names
        safe_user_id = re.sub(r'[^\w\-.]', '_', user_id)
        safe_policy_id = re.sub(r'[^\w\-.]', '_', policy_id)
        return self.base_path / safe_user_id / safe_policy_id

    def _get_consent_filepath(self, consent: UserConsent) -> Path:
        consent_dir = self._get_consent_dir_path(consent.user_id, consent.policy_id)
        # Sanitize consent_id and timestamp for filename
        safe_consent_id = re.sub(r'[^\w\-.]', '_', consent.consent_id)
        # Ensure timestamp is a valid filename component, replace colons, etc.
        safe_timestamp = consent.timestamp.replace(":", "-").replace("+", "ZPLUS").replace(".", "DOT")
        return consent_dir / f"{safe_consent_id}_{safe_timestamp}.json"

    def save_consent(self, consent: UserConsent) -> bool:
        if not isinstance(consent, UserConsent):
            raise ValueError("Invalid consent object provided.")
        if not consent.user_id or not consent.policy_id or not consent.consent_id or not consent.timestamp:
            raise ValueError("Consent object is missing required fields (user_id, policy_id, consent_id, timestamp).")

        filepath = self._get_consent_filepath(consent)
        self._ensure_dir_exists(filepath.parent) # Ensure directory user_id/policy_id exists

        try:
            with open(filepath, 'w') as f:
                json.dump(consent.to_dict(), f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving consent {consent.consent_id}: {e}")
            return False

    def load_consents_for_user_policy(self, user_id: str, policy_id: str) -> List[UserConsent]:
        consent_dir = self._get_consent_dir_path(user_id, policy_id)
        if not consent_dir.exists() or not consent_dir.is_dir():
            return []

        consents = []
        pattern = consent_dir / "*.json"
        for filepath_str in glob.glob(str(pattern)):
            filepath = Path(filepath_str)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    consents.append(UserConsent.from_dict(data))
            except (IOError, json.JSONDecodeError, ValueError) as e:
                print(f"Error loading or parsing consent file {filepath}: {e}")

        # Sort by timestamp, most recent first
        consents.sort(key=lambda c: c.timestamp, reverse=True)
        return consents

    def load_latest_active_consent(self, user_id: str, policy_id: str) -> Optional[UserConsent]:
        all_consents_for_policy = self.load_consents_for_user_policy(user_id, policy_id)
        for consent_record in all_consents_for_policy: # Already sorted newest first
            if consent_record.is_active:
                # Check for expiration
                if consent_record.expires_at:
                    try:
                        # Ensure correct parsing of ISO format, potentially with 'Z'
                        expires_at_str = consent_record.expires_at
                        if expires_at_str.endswith('Z'):
                            expiration_date = datetime.fromisoformat(expires_at_str[:-1] + '+00:00')
                        else:
                            expiration_date = datetime.fromisoformat(expires_at_str)

                        # If expires_at was naive, assume UTC (common for ISO strings ending in Z)
                        if expiration_date.tzinfo is None or expiration_date.tzinfo.utcoffset(expiration_date) is None:
                             expiration_date = expiration_date.replace(tzinfo=timezone.utc)

                        current_time_utc = datetime.now(timezone.utc)
                        if expiration_date < current_time_utc:
                            # Optionally, mark as inactive and re-save if this store should manage state
                            # consent_record.is_active = False
                            # self.save_consent(consent_record) # This could lead to loops or complexity
                            continue # Skip this expired consent
                    except ValueError as e:
                        print(f"Error parsing expires_at for consent {consent_record.consent_id}: {e}")
                        # Treat as non-expiring or handle error as per policy
                return consent_record
        return None

    def load_all_consents_for_user(self, user_id: str) -> List[UserConsent]:
        safe_user_id = re.sub(r'[^\w\-.]', '_', user_id)
        user_dir = self.base_path / safe_user_id
        if not user_dir.exists() or not user_dir.is_dir():
            return []

        all_user_consents = []
        for policy_dir_path in user_dir.iterdir():
            if policy_dir_path.is_dir():
                # Extract original policy_id - this is tricky if it was sanitized.
                # For now, assume dir name is the (potentially sanitized) policy_id.
                # A better system would store original policy_id in a manifest or use it directly as dir name if safe.
                policy_id_from_dir = policy_dir_path.name # This is the sanitized policy_id

                # To get the original policy_id, we'd need to map it back or load a consent to find it.
                # This is a limitation of the current simplified dir naming.
                # For this method, we'll load consents and use the policy_id from the consent object.
                # This means we iterate more files than strictly necessary if we only need policy_id.

                pattern = policy_dir_path / "*.json"
                for filepath_str in glob.glob(str(pattern)):
                    filepath = Path(filepath_str)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            all_user_consents.append(UserConsent.from_dict(data))
                    except (IOError, json.JSONDecodeError, ValueError) as e:
                         print(f"Error loading or parsing consent file {filepath}: {e}")

        all_user_consents.sort(key=lambda c: c.timestamp, reverse=True)
        return all_user_consents


if __name__ == '__main__':
    import tempfile
    import shutil
    from datetime import timedelta # Ensure this is imported for examples

    temp_dir_consents = tempfile.mkdtemp()
    print(f"Using temporary directory for ConsentStore: {temp_dir_consents}")
    consent_store = ConsentStore(base_path=temp_dir_consents)

    # Sample consents
    user1 = "userABC"
    user2 = "userXYZ/special"
    policyA = "PolicyID-Main"
    policyB = "PolicyID-Other"

    # Timestamps for ordering
    ts_now = datetime.now(timezone.utc)
    ts_yesterday = ts_now - timedelta(days=1)
    ts_two_days_ago = ts_now - timedelta(days=2)
    ts_expires_soon = ts_now + timedelta(minutes=1)
    ts_expired = ts_now - timedelta(minutes=1)


    c1 = UserConsent(user_id=user1, policy_id=policyA, policy_version="1.0", timestamp=ts_two_days_ago.isoformat())
    c2_active = UserConsent(user_id=user1, policy_id=policyA, policy_version="1.1", timestamp=ts_yesterday.isoformat())
    c3_expired = UserConsent(user_id=user1, policy_id=policyA, policy_version="1.2", timestamp=ts_now.isoformat(), is_active=True, expires_at=ts_expired.isoformat())
    c4_expires_soon = UserConsent(user_id=user1, policy_id=policyA, policy_version="1.3", timestamp=ts_now.isoformat(), is_active=True, expires_at=ts_expires_soon.isoformat()) # Should be active initially

    c5_user1_policyB = UserConsent(user_id=user1, policy_id=policyB, policy_version="1.0", timestamp=ts_now.isoformat())
    c6_user2_policyA = UserConsent(user_id=user2, policy_id=policyA, policy_version="1.1", timestamp=ts_now.isoformat())

    # Save consents
    print(f"Saving c1: {consent_store.save_consent(c1)}")
    print(f"Saving c2_active: {consent_store.save_consent(c2_active)}")
    print(f"Saving c3_expired: {consent_store.save_consent(c3_expired)}") # Will be active at save time
    print(f"Saving c4_expires_soon: {consent_store.save_consent(c4_expires_soon)}")
    print(f"Saving c5_user1_policyB: {consent_store.save_consent(c5_user1_policyB)}")
    print(f"Saving c6_user2_policyA: {consent_store.save_consent(c6_user2_policyA)}")

    # Load consents for user1, policyA
    u1pA_consents = consent_store.load_consents_for_user_policy(user1, policyA)
    print(f"\nConsents for {user1}, {policyA} (count: {len(u1pA_consents)}):")
    for c in u1pA_consents:
        print(f"  ID: {c.consent_id}, TS: {c.timestamp}, Active: {c.is_active}, Expires: {c.expires_at}")
    assert len(u1pA_consents) == 4
    assert u1pA_consents[0].consent_id == c4_expires_soon.consent_id or u1pA_consents[0].consent_id == c3_expired.consent_id # Timestamps are same for c3, c4

    # Load latest active for user1, policyA
    latest_active_u1pA = consent_store.load_latest_active_consent(user1, policyA)
    print(f"\nLatest active for {user1}, {policyA}:")
    if latest_active_u1pA:
        print(f"  ID: {latest_active_u1pA.consent_id}, TS: {latest_active_u1pA.timestamp}, Expires: {latest_active_u1pA.expires_at}")
        assert latest_active_u1pA.consent_id == c4_expires_soon.consent_id # c3 is expired, c4 is not yet
    else:
        print("  None found.")
        assert False, "c4_expires_soon should be the latest active"

    # Simulate time passing for c4_expires_soon to expire
    print("\nSimulating time passing for c4_expires_soon to expire...")
    # For test, we can't actually wait. We assume the logic in load_latest_active_consent handles it.
    # To truly test expiration, we'd need to mock datetime.now or set expires_at to the past.
    # The c3_expired already tests this. Let's verify c3_expired is not returned as active.

    # Make c4 expired for a more direct test of fallback
    c4_expires_soon.is_active = True # ensure it was active
    c4_expires_soon.expires_at = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    consent_store.save_consent(c4_expires_soon) # Resave it as expired

    latest_active_u1pA_after_c4_expiry = consent_store.load_latest_active_consent(user1, policyA)
    print(f"\nLatest active for {user1}, {policyA} (after c4 expired):")
    if latest_active_u1pA_after_c4_expiry:
        print(f"  ID: {latest_active_u1pA_after_c4_expiry.consent_id}, TS: {latest_active_u1pA_after_c4_expiry.timestamp}")
        assert latest_active_u1pA_after_c4_expiry.consent_id == c2_active.consent_id # Should fall back to c2
    else:
        print("  None found.")
        assert False, "Should have fallen back to c2_active"


    # Load all consents for user1
    all_u1_consents = consent_store.load_all_consents_for_user(user1)
    print(f"\nAll consents for {user1} (count: {len(all_u1_consents)}):")
    # Expected 5: 4 for PolicyA, 1 for PolicyB
    assert len(all_u1_consents) == 5
    for c in all_u1_consents:
        print(f"  ID: {c.consent_id}, Policy: {c.policy_id}, TS: {c.timestamp}")


    # Load consents for user2 (with special char in ID)
    u2_consents = consent_store.load_all_consents_for_user(user2)
    print(f"\nAll consents for '{user2}' (count: {len(u2_consents)}):")
    assert len(u2_consents) == 1
    if u2_consents:
        assert u2_consents[0].consent_id == c6_user2_policyA.consent_id
        print(f"  ID: {u2_consents[0].consent_id}, Policy: {u2_consents[0].policy_id}")


    # Test loading non-existent
    no_consents = consent_store.load_consents_for_user_policy("NoUser", "NoPolicy")
    print(f"\nConsents for NoUser, NoPolicy: {no_consents}")
    assert len(no_consents) == 0
    latest_active_none = consent_store.load_latest_active_consent("NoUser", "NoPolicy")
    assert latest_active_none is None


    # Clean up
    try:
        shutil.rmtree(temp_dir_consents)
        print(f"\nCleaned up temporary directory: {temp_dir_consents}")
    except Exception as e:
        print(f"Error cleaning up temp directory {temp_dir_consents}: {e}")

    print("\nConsentStore examples finished.")
