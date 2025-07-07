import uuid
import random
from datetime import datetime, timezone

class MockDataGenerator:
    def __init__(self):
        self.first_names = ["Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona"]
        self.last_names = ["Smith", "Jones", "Williams", "Brown", "Davis", "Miller"]
        self.domains = ["example.com", "mailservice.net", "webhost.org", "demo.co"]
        self.pages = ["/home", "/products", "/services", "/contact", "/profile", "/settings"]
        self.search_terms = ["privacy protocol", "data security", "ai ethics", "digital identity", "secure storage"]
        self.ips = [f"192.168.1.{random.randint(1,254)}", f"10.0.0.{random.randint(1,254)}", f"172.16.31.{random.randint(1,254)}"]
        self.cities = ["New York", "London", "Paris", "Tokyo", "Berlin", "San Francisco"]
        self.countries = ["USA", "UK", "France", "Japan", "Germany"]

    def _get_random_user_id(self, user_id_prefix="user_"):
        return f"{user_id_prefix}{str(uuid.uuid4())[:8]}"

    def generate_user_login_event(self, user_id: str = None):
        uid = user_id if user_id else self._get_random_user_id()
        return {
            "event_type": "user_login",
            "user_id": uid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ip_address": random.choice(self.ips),
            "user_agent": f"Mozilla/5.0 (DemoBrowser {random.randint(1,10)}.0)"
        }

    def generate_page_view_event(self, user_id: str = None, page_url: str = None):
        uid = user_id if user_id else self._get_random_user_id()
        return {
            "event_type": "page_view",
            "user_id": uid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "page_url": page_url if page_url else random.choice(self.pages),
            "referrer": random.choice(self.pages + [None, "external_site.com/link"]),
            "ip_address": random.choice(self.ips)
        }

    def generate_search_event(self, user_id: str = None):
        uid = user_id if user_id else self._get_random_user_id()
        return {
            "event_type": "search",
            "user_id": uid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "search_query": random.choice(self.search_terms),
            "results_count": random.randint(0, 50)
        }

    def generate_user_profile_data(self, user_id: str = None, include_optional: bool = True):
        uid = user_id if user_id else self._get_random_user_id("profile_")
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        profile = {
            "user_id": uid,
            "email": f"{first.lower()}.{last.lower()}@{random.choice(self.domains)}",
            "full_name": f"{first} {last}",
            "registration_date": (datetime.now(timezone.utc) - timedelta(days=random.randint(1,365))).isoformat(),
            "last_login_ip": random.choice(self.ips)
        }
        if include_optional:
            if random.choice([True, False]):
                profile["phone_number"] = f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}"
            if random.choice([True, False]):
                profile["city"] = random.choice(self.cities)
            if random.choice([True, False]):
                profile["country"] = random.choice(self.countries)
            if random.choice([True, False]):
                profile["postal_code"] = str(random.randint(10000,99999))
            if random.choice([True, False]):
                 profile["preferences"] = {"theme": random.choice(["dark", "light"]), "notifications": random.choice([True, False])}
        return profile

    def generate_sensor_data(self, device_id: str = None):
        did = device_id if device_id else f"sensor_{str(uuid.uuid4())[:6]}"
        return {
            "event_type": "sensor_reading",
            "device_id": did,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": round(random.uniform(20.0, 50.0), 6), # Example range (e.g. USA)
            "longitude": round(random.uniform(-120.0, -70.0), 6),
            "temperature_celsius": round(random.uniform(15.0, 30.0), 1),
            "battery_level": round(random.uniform(0.1, 1.0), 2)
        }

if __name__ == '__main__':
    from datetime import timedelta # Ensure timedelta is imported for example
    generator = MockDataGenerator()

    print("--- Sample User Login Event ---")
    print(generator.generate_user_login_event("user123"))

    print("\n--- Sample Page View Event ---")
    print(generator.generate_page_view_event())

    print("\n--- Sample Search Event ---")
    print(generator.generate_search_event("user789"))

    print("\n--- Sample User Profile Data (Full) ---")
    print(generator.generate_user_profile_data())

    print("\n--- Sample User Profile Data (Minimal) ---")
    print(generator.generate_user_profile_data(include_optional=False))

    print("\n--- Sample Sensor Data ---")
    print(generator.generate_sensor_data("deviceABC"))

    print("\nAll MockDataGenerator examples executed.")
