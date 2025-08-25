import google.generativeai as genai
import json
from . import database

# Load configuration
with open("config.json") as file:
    config = json.load(file)

# AI Configuration
genai.configure(api_key=config["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def get_ai_response(query, user_id):
    """Gets a response from Gemini, potentially with user context."""
    # Future enhancement: Load user-specific context from DB to enrich the prompt
    # For now, it's a direct query.
    try:
        response = model.generate_content(query)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "I'm having trouble connecting to my brain right now."

def process_query_for_user(user_id, query):
    """The main logic hub for processing any user query."""
    query = query.lower()

    # 1. Check for memory-related commands first
    if 'remember that' in query:
        try:
            # e.g., "remember that my favorite color is blue"
            data = query.split('remember that ')[1]
            key, value = data.split(' is ')
            database.save_memory(user_id, key.strip(), value.strip())
            return f"Got it. I'll remember that {key.strip()} is {value.strip()}."
        except Exception as e:
            return "I didn't quite catch that. Please try saying it like 'remember that my pin is 1234'."

    elif 'what is' in query or 'who is' in query:
        try:
            # e.g., "what is my favorite color"
            key = query.replace('what is', '').replace('who is', '').strip()
            memory = database.get_memory(user_id, key)
            if memory:
                return f"You told me that {key} is {memory}."
            else:
                # If not in local memory, fall back to Gemini
                return get_ai_response(query, user_id)
        except Exception as e:
            return "I'm not sure how to answer that."

    # 2. Add other specific commands here (Spotify, Weather, etc.)
    # Example:
    # elif 'play' in query:
    #     song_name = query.replace('play', '').strip()
    #     # Call your spotify function here
    #     return f"Playing {song_name}..."

    # 3. If no specific command is matched, default to the AI
    else:
        return get_ai_response(query, user_id)