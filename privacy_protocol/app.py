import os
from flask import Flask, render_template, request
from privacy_protocol.interpreter import PrivacyInterpreter

app = Flask(__name__)

# Initialize the interpreter
# spaCy model loading messages might appear in the console here if the model is not found
# or needs to be downloaded.
interpreter = PrivacyInterpreter()

# Construct the absolute path to keywords.json relative to this app.py file
# __file__ is the path to app.py
# os.path.dirname(__file__) is the directory 'privacy_protocol/'
# os.path.join will create 'privacy_protocol/data/keywords.json'
KEYWORDS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'keywords.json')

# Load keywords once when the app starts
# Subsequent calls to analyze_text will use these loaded keywords.
# If keywords.json can change while the app is running, this should be moved into the /analyze route.
interpreter.load_keywords_from_path(KEYWORDS_FILE_PATH)
app.interpreter = interpreter # Attach interpreter to the app object

if not app.interpreter.keywords_data:
    print(f"WARNING: Keywords not loaded from {KEYWORDS_FILE_PATH}. Analysis might not work as expected.")
if app.interpreter.nlp is None:
    print("WARNING: spaCy NLP model not loaded. Clause detection will be basic or disabled.")


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    policy_text = request.form.get('policy_text', '')

    # Keywords are already loaded at startup.
    # If keywords.json could change dynamically, you might reload them here:
    # interpreter.load_keywords_from_path(KEYWORDS_FILE_PATH)
    # if not interpreter.keywords_data:
    #     # Handle error - perhaps render results with an error message
    #     return "Error: Could not load keywords.json", 500

    analysis_results = []
    nlp_available = app.interpreter.nlp is not None
    if policy_text.strip():
        if not nlp_available:
            # Optionally, provide a specific message if NLP isn't working
            # For now, analyze_text handles this by returning empty or limited results
            pass
        analysis_results = app.interpreter.analyze_text(policy_text)

    return render_template('results.html', policy_text=policy_text, analysis_results=analysis_results, nlp_available=nlp_available)

if __name__ == '__main__':
    # Note: For development, use `flask run`.
    # `app.run()` is also possible but `flask run` is preferred for development.
    # Example: FLASK_APP=app.py flask run --host=0.0.0.0 --port=5000
    # The host and port here are for direct `python app.py` execution if needed.
    app.run(debug=True, host='0.0.0.0', port=5000)
