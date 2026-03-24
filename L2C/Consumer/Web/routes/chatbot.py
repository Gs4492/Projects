from flask import Blueprint, render_template, request, jsonify
import spacy
from Shared.chatbot_responses import responses, default_response

chatbot_bp = Blueprint('chatbot', __name__)
nlp = spacy.load("en_core_web_sm")

@chatbot_bp.route('/chatbot')
def chatbot():
    return render_template('layout/chatbot.html')

@chatbot_bp.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    user_message = data.get('message', '')
    doc = nlp(user_message.lower())

    cleaned_input = " ".join([
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct
    ])

    bot_response = default_response
    for keyword, reply in responses.items():
        if keyword in cleaned_input:
            bot_response = reply
            break

    return jsonify({'response': bot_response})
