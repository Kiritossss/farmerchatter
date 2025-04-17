from flask import Flask, render_template, request, jsonify
import json
from googletrans import Translator
import os
import difflib

app = Flask(__name__)
translator = Translator()

# Load and normalize the knowledge base
with open("knowledge_base.json", "r", encoding="utf-8") as file:
    raw_kb = json.load(file)
    kb = {key.strip().lower(): value for key, value in raw_kb.items()}

# Normalize helper
def normalize(text):
    return text.strip().lower()

# Translate to English
def translate_to_english(text):
    try:
        return translator.translate(text, dest='en').text
    except:
        return text

# Detect user language
def detect_language(text):
    try:
        return translator.detect(text).lang
    except:
        return "en"

# Translate back to original language
def translate_back(text, target_lang):
    try:
        return translator.translate(text, dest=target_lang).text
    except:
        return text

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot_response():
    user_input = request.json.get("message")
    original_lang = detect_language(user_input)
    
    english_input = translate_to_english(user_input)
    normalized_input = normalize(english_input)

    # Try direct match
    response = kb.get(normalized_input)

    # If not found, try fuzzy match
    if not response:
        possible_matches = difflib.get_close_matches(normalized_input, kb.keys(), n=1, cutoff=0.6)
        if possible_matches:
            response = kb[possible_matches[0]]
        else:
            response = "Sorry, I don't have an answer for that yet."

    # Translate back to original language if needed
    if original_lang != 'en':
        response = translate_back(response, original_lang)

    return jsonify({"reply": response})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
