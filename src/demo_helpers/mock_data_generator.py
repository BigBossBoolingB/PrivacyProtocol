import random
import datetime
from typing import Dict, Any

class MockDataGenerator:
    """
    Generates realistic sample data that could contain PII or sensitive information.
    """

    @staticmethod
    def generate_user_activity_record() -> Dict[str, Any]:
        """
        Generates a dictionary representing a user activity event.
        """
        user_ids = ["user_a", "user_b", "user_c"]
        events = ["login", "page_view", "search_query", "purchase"]
        products = ["product_x", "product_y", "product_z"]
        queries = ["how to bake a cake", "best laptops 2024", "python tutorial"]

        event = random.choice(events)
        user_id = random.choice(user_ids)

        record = {
            "user_id": user_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "ip_address": f"192.168.1.{random.randint(1, 254)}",
            "location": random.choice(["New York", "London", "Tokyo"]),
            "email": f"{user_id}@example.com",
            "event_type": event,
        }

        if event == "search_query":
            record["query_text"] = random.choice(queries)
        elif event == "purchase":
            record["product_id"] = random.choice(products)
            record["price"] = round(random.uniform(10.0, 1000.0), 2)

        return record
