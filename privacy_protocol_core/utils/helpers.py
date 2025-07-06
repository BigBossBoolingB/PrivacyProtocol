# Utility functions for the Privacy Protocol application

import re
import datetime

def sanitize_text(text):
    """
    Basic text sanitization: removes excessive whitespace.
    More advanced sanitization (e.g., HTML stripping) might be needed.
    """
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_current_timestamp_iso():
    """Returns the current timestamp in ISO 8601 format."""
    return datetime.datetime.now().isoformat()

def extract_domain(url):
    """
    Extracts the domain name from a URL.
    Example: "http://www.example.com/path" -> "example.com"
    """
    if not url:
        return None
    try:
        from urllib.parse import urlparse
        parsed_uri = urlparse(url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        # Remove 'www.' if present
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return None # Or handle error as appropriate

# Example of a more specific helper, could be moved to a relevant module later
def is_clause_related_to_data_selling(clause_text):
    """
    A very basic check to see if a clause might be related to data selling.
    This would be significantly more complex in a real NLP implementation.
    """
    keywords = ["sell", "sells", "sold", "data broker", "third-party marketing", "affiliate sharing for profit"]
    clause_lower = clause_text.lower()
    for keyword in keywords:
        if keyword in clause_lower:
            return True
    return False

if __name__ == '__main__':
    # Test cases for helpers
    print("Sanitize Test:")
    print(f"'  Extra   spaces  ' -> '{sanitize_text('  Extra   spaces  ')}'")

    print("\nTimestamp Test:")
    print(f"Current ISO Timestamp: {get_current_timestamp_iso()}")

    print("\nExtract Domain Test:")
    print(f"'http://www.example.com/path' -> '{extract_domain('http://www.example.com/path')}'")
    print(f"'https://sub.example.co.uk/another?q=1' -> '{extract_domain('https://sub.example.co.uk/another?q=1')}'")
    print(f"'invalid-url' -> '{extract_domain('invalid-url')}'") # Should ideally be None or handle error

    print("\nData Selling Clause Test:")
    test_clause_positive = "We may sell your personal information to data brokers for their marketing purposes."
    test_clause_negative = "We value your privacy and do not share your data."
    print(f"'{test_clause_positive[:30]}...' -> Selling related? {is_clause_related_to_data_selling(test_clause_positive)}")
    print(f"'{test_clause_negative[:30]}...' -> Selling related? {is_clause_related_to_data_selling(test_clause_negative)}")
