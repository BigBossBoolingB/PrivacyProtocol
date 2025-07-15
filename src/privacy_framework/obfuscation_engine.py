from typing import Dict, Any

class ObfuscationEngine:
    """
    Obfuscates data based on its classification.
    """
    @staticmethod
    def obfuscate_data(data: Dict[str, Any], classified_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Obfuscates data based on its classification.

        Args:
            data (Dict[str, Any]): The data to obfuscate.
            classified_data (Dict[str, str]): The classification of the data.

        Returns:
            Dict[str, Any]: The obfuscated data.
        """
        obfuscated_data = data.copy()
        for key, classification in classified_data.items():
            if classification == "sensitive":
                obfuscated_data[key] = "********"
        return obfuscated_data
