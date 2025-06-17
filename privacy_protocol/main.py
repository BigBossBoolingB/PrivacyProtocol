import argparse
import os
from privacy_protocol.interpreter import PrivacyInterpreter

def main():
    parser = argparse.ArgumentParser(description="Privacy Protocol: Analyze privacy policy text.")
    parser.add_argument("file", nargs='?', help="Path to the text file containing the privacy policy. If not provided, uses sample text.")
    parser.add_argument("--keywords", default="data/keywords.json", help="Path to the keywords JSON file.")

    args = parser.parse_args()

    # Construct the absolute path to the keywords file
    # This assumes main.py is in the root 'privacy_protocol' directory
    # and 'data' is a subdirectory at the same level.
    keywords_path = os.path.join(os.path.dirname(__file__), args.keywords)

    # If running from the root of the project (e.g. `python main.py`),
    # the path might need adjustment if interpreter.py expects it relative to its own location.
    # For now, let's ensure interpreter can load it directly or we adjust path here.

    interpreter = PrivacyInterpreter() # Initialize without path first
    interpreter.load_keywords_from_path(keywords_path) # Load with correct path


    if not interpreter.keywords_data:
        print(f"Could not load keywords from {keywords_path}. Please check the file and path.")
        return

    policy_text = ""
    if args.file:
        try:
            with open(args.file, 'r') as f:
                policy_text = f.read()
        except FileNotFoundError:
            print(f"Error: Policy file not found at {args.file}")
            return
    else:
        print("No policy file provided. Using sample text for demonstration:")
        policy_text = """
        This is a sample privacy policy. We may share your data with a third-party for analytics.
        We will not engage in data selling. However, we use cookies for tracking purposes.
        Sometimes we use anonymized data for research. Our commitment to your privacy is paramount.
        We strive to be transparent about how we collect and use your information, including any
        third-party sharing for service improvement. We avoid data selling practices.
        """
        print("-------------------------")
        print(policy_text)
        print("-------------------------")


    if not policy_text.strip():
        print("The policy text is empty. Nothing to analyze.")
        return

    analysis_results = interpreter.analyze_text(policy_text)

    if analysis_results:
        print("\n--- Privacy Analysis Results ---")
        for item in analysis_results:
            print(f"** Keyword Found: {item['keyword']} **")
            print(f"   Category: {item['category']}")
            print(f"   Explanation: {item['explanation']}\n")
    else:
        print("No concerning keywords found in the provided text.")

if __name__ == "__main__":
    main()
