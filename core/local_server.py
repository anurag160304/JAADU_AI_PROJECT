from flask import Flask, request, jsonify
from . import ai_brain
from . import database

app = Flask(__name__)

@app.route('/api/interact', methods=['POST'])
def handle_interaction():
    data = request.json
    user_id = data.get('userId')
    query = data.get('query')

    if not user_id or not query:
        return jsonify({"error": "userId and query are required"}), 400

    response_text = ai_brain.process_query_for_user(user_id, query)
    return jsonify({"response": response_text})

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.json
    username = data.get('username').lower()

    if not username:
        return jsonify({"error": "username is required"}), 400

    user_id = database.get_user(username)
    if user_id:
        return jsonify({"userId": user_id, "message": f"Welcome back, {username.capitalize()}."})
    else:
        # Create new user
        new_user_id = database.add_user(username)
        if new_user_id:
            return jsonify({"userId": new_user_id, "message": f"Created a new profile for you, {username.capitalize()}."})
        else:
            return jsonify({"error": "Could not create or find user."}), 500

def run_server():
    # Runs on all network interfaces, accessible from your phone
    app.run(host='0.0.0.0', port=5000)