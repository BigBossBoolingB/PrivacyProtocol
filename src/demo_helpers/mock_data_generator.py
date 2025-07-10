# src/demo_helpers/mock_data_generator.py
"""
Generates mock data for demonstration purposes.
"""
import random
import time
import uuid

class MockDataGenerator:
    """
    Generates various types of mock data records.
    """
    def __init__(self, user_ids: Optional[List[str]] = None, device_ids: Optional[List[str]] = None):
        self.user_ids = user_ids or ["user_alpha", "user_beta", "user_gamma"]
        self.device_ids = device_ids or ["device_A100", "device_B200", "device_C300"]
        self.actions = ["login", "page_view", "search_query", "item_view", "add_to_cart", "purchase"]
        self.pages = ["/home", "/products/123", "/products/456", "/cart", "/checkout", "/profile"]
        self.search_terms = ["privacy tools", "best vpn", "secure email", "data encryption"]
        self.item_categories = ["electronics", "books", "clothing", "home_goods"]
        self.ips = ["192.168.1.10", "10.0.0.5", "172.16.5.20", "203.0.113.45"]
        self.emails = ["alpha@example.com", "beta@example.org", "gamma@example.net", "delta@example.com"]
        self.cities = ["New York", "London", "Paris", "Tokyo", "Berlin"]


    def _get_random_user(self) -> str:
        return random.choice(self.user_ids)

    def _get_random_device(self) -> str:
        return random.choice(self.device_ids)

    def _get_current_timestamp(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def generate_user_activity_event(self) -> Dict[str, Any]:
        """Generates a mock user activity event."""
        user_id = self._get_random_user()
        action = random.choice(self.actions)
        event: Dict[str, Any] = {
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "timestamp": self._get_current_timestamp(),
            "ip_address": random.choice(self.ips),
            "user_agent": f"DemoBrowser/1.{random.randint(0,9)} (Compatible; PrivacyProtocolDemo)"
        }

        if action == "login":
            event["login_successful"] = random.choice([True, False])
            event["email"] = random.choice(self.emails) # Login might involve email
        elif action == "page_view":
            event["page_url"] = random.choice(self.pages)
            event["referrer_url"] = random.choice([None, "https://external-site.com/link", "/previous-page"])
        elif action == "search_query":
            event["query"] = random.choice(self.search_terms)
            event["results_count"] = random.randint(0, 100)
        elif action == "item_view":
            event["item_id"] = f"item_{random.randint(100,999)}"
            event["item_category"] = random.choice(self.item_categories)
        elif action == "add_to_cart":
            event["item_id"] = f"item_{random.randint(100,999)}"
            event["quantity"] = random.randint(1, 5)
            event["price_per_item"] = round(random.uniform(5.0, 200.0), 2)
        elif action == "purchase":
            event["order_id"] = f"ORD-{random.randint(10000,99999)}"
            event["total_amount"] = round(random.uniform(20.0, 500.0), 2)
            event["currency"] = "USD"
            event["item_count"] = random.randint(1,10)
            # Potentially include email for receipt
            if random.random() < 0.7: # 70% chance to include email
                 event["customer_email"] = random.choice(self.emails)
            # Potentially include shipping address details (as a sub-dictionary)
            if random.random() < 0.5:
                event["shipping_address"] = {
                    "street": f"{random.randint(1,1000)} Main St",
                    "city": random.choice(self.cities),
                    "zip_code": str(random.randint(10000,99999))
                }
        return event

    def generate_sensor_reading(self) -> Dict[str, Any]:
        """Generates a mock sensor reading."""
        device_id = self._get_random_device()
        reading: Dict[str, Any] = {
            "reading_id": str(uuid.uuid4()),
            "device_id": device_id,
            "timestamp": self._get_current_timestamp(),
            "sensor_type": random.choice(["temperature", "humidity", "gps_location", "motion"]),
        }
        if reading["sensor_type"] == "temperature":
            reading["value"] = round(random.uniform(-10.0, 40.0), 1) # Celsius
            reading["unit"] = "C"
        elif reading["sensor_type"] == "humidity":
            reading["value"] = round(random.uniform(20.0, 80.0), 1) # Percent
            reading["unit"] = "%"
        elif reading["sensor_type"] == "gps_location":
            reading["location"] = { # More specific key for classifier
                "latitude": round(random.uniform(-90.0, 90.0), 6),
                "longitude": round(random.uniform(-180.0, 180.0), 6),
                "altitude": random.choice([None, round(random.uniform(0, 1000), 1)])
            }
        elif reading["sensor_type"] == "motion":
            reading["detected"] = random.choice([True, False])
            if reading["detected"]:
                reading["intensity"] = random.randint(1,10)

        return reading

if __name__ == '__main__':
    generator = MockDataGenerator()
    print("--- Sample User Activity Events ---")
    for _ in range(3):
        print(json.dumps(generator.generate_user_activity_event(), indent=2))
        print("-" * 20)

    print("\n--- Sample Sensor Readings ---")
    for _ in range(3):
        print(json.dumps(generator.generate_sensor_reading(), indent=2))
        print("-" * 20)
