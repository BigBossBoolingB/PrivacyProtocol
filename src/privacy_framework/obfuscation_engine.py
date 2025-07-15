from typing import Dict, Any

class ObfuscationEngine:
    @staticmethod
    def obfuscate_data(data: Dict[str, Any], classified_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Obfuscates data based on its classification.
        """
        obfuscated_data = data.copy()
        for key, classification in classified_data.items():
            if classification == "sensitive":
                obfuscated_data[key] = "********"
        return obfuscated_data
