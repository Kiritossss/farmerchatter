from flask import Flask, render_template, request, jsonify
import json
from googletrans import Translator
import difflib
import os

app = Flask(__name__)
translator = Translator()

# Load and normalize knowledge base
with open("knowledge_base.json", "r", encoding="utf-8") as file:
    raw_kb = json.load(file)
    kb = {q.strip().lower(): a.strip() for q, a in raw_kb.items()}

# Helper functions
def normalize(text):
    return text.strip().lower()

def translate_to_english(text):
    try:
        return translator.translate(text, dest='en').text
    except:
        return text

def detect_language(text):
    try:
        return translator.detect(text).lang
    except:
        return "en"

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
    user_lang = detect_language(user_input)

    english_input = translate_to_english(user_input)
    normalized_input = normalize(english_input)

    response = kb.get(normalized_input)

    if not response:
        matches = difflib.get_close_matches(normalized_input, kb.keys(), n=1, cutoff=0.6)
        if matches:
            response = kb[matches[0]]
        else:
            response = "Sorry, I don't have an answer for that yet."

    # Translate back to Hindi if user asked in Hindi
    if user_lang != "en":
        response = translate_back(response, user_lang)

    return jsonify({"reply": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
