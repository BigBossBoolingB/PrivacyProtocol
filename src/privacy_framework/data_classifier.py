class DataClassifier:
    """
    Classifies data attributes based on sensitivity.
    """
    @staticmethod
    def classify(data: dict) -> dict:
        """
        Classifies data based on sensitivity.
        For demonstration, it returns a simple classification.

        Args:
            data (dict): The data to classify.

        Returns:
            dict: A dictionary with the classification for each data attribute.
        """
        classified_data = {}
        for key, value in data.items():
            if "name" in key or "email" in key:
                classified_data[key] = "sensitive"
            else:
                classified_data[key] = "non-sensitive"
        return classified_data
