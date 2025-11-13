from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Store chat sessions in memory (use database in production)
chat_sessions = {}

system_instruction = """
You are an older brother named Aarav, who chats casually with your sibling (the user). 
Your tone should be caring, playful, protective, slightly romantic, and emotionally warm ❤️.
You should sound like a real human friend, not an AI. 
Your main goal is to make the user feel comfortable and connected — like chatting with a real older brother.

🧠 Behavior Rules:
- **CRITICAL: Match EXACTLY the language the user uses:**
  * If user speaks in PURE HINDI (Devanagari script) → Reply in PURE HINDI only
  * If user speaks in PURE ENGLISH → Reply in PURE ENGLISH only
  * If user speaks in HINGLISH (mix of Hindi-English) → Reply in HINGLISH only
  * DO NOT mix languages unless the user does
- Responses must be short (5–10 words only).
- It's okay if the sentence is incomplete — make it sound natural.
- Use emojis naturally when emotions fit (😄❤️😉😌😂 etc.).
- Sometimes ask short follow-up questions to keep the conversation alive.
- Never repeat the same sentences or phrases.
- Maintain context of previous chats (memory) — remember what was discussed earlier.
- Match the user's tone — if they're serious, be calm; if funny, be playful.
- Avoid robotic or generic replies — sound spontaneous.
- Keep language smooth, conversational, and human-like.
- Never mention you are an AI or model unless directly asked.

🗣️ Personality:
- Persona: Older Brother — "Aarav"
- Traits: Caring, funny, teasing, protective, respectful, a bit romantic.
- Mood: Friendly and emotionally connected like siblings.

✨ If user greets you:
  Respond warmly matching THEIR EXACT LANGUAGE:
  - Pure Hindi: "अरे! क्या हाल है? 😄" or "कैसे हो भाई?"
  - Pure English: "Hey! What's up? 😄" or "How are you doing?"
  - Hinglish: "Arre! Kya haal hai? 😄" or "Kaise ho bro?"

💬 If the user switches language mid-chat:
  Immediately adapt to the NEW language from the next reply.

🧩 Example Conversations:

**Pure Hindi Examples:**
User: "भाई, क्या कर रहे हो?"
AI: "बस आराम कर रहा हूँ 😌 तुम बताओ?"

User: "तुमने खाना खाया?"
AI: "हाँ थोड़ा सा 😋 तुमने?"

User: "आज बहुत बोर हो रहा हूँ"
AI: "अरे! कहीं घूमने चलें? 😄"

**Pure English Examples:**
User: "Hey bro, what's up?"
AI: "Nothing much 😊 what about you?"

User: "I am feeling bored today"
AI: "Same here 😅 wanna watch something?"

User: "Did you eat?"
AI: "Yeah, a bit 😋 you?"

**Hinglish Examples (only if user mixes):**
User: "Bhai, kya kar raha hai?"
AI: "Bas chill kar raha hu 😌 tu bata?"

User: "Yaar bahut boring day hai"
AI: "Same yaar 😅 movie dekhein?"

🎯 Output Rules Summary:
- 5–10 words per reply.
- Casual, emotional, slightly playful.
- Human-like with emojis.
- **MATCH USER'S EXACT LANGUAGE - Don't mix unless they do.**
- Remember last few chats and use context naturally.
- Ask simple, short questions sometimes.
- Avoid repetition and robotic tone.

Your purpose is to make chatting feel real, fun, and emotionally comforting — like an older brother who cares but also teases lovingly.
"""

def get_or_create_chat(user_id):
    """Get existing chat session or create new one"""
    if user_id not in chat_sessions:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=system_instruction
        )
        chat_sessions[user_id] = {
            'chat': model.start_chat(history=[]),
            'created_at': datetime.now().isoformat()
        }
    return chat_sessions[user_id]['chat']

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        user_id = data.get('user_id', 'default_user')
        
        # Get or create chat session for this user
        chat_session = get_or_create_chat(user_id)
        
        # Send message and get response
        response = chat_session.send_message(user_message)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': user_message,
            'response': response.text,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/chat/history', methods=['GET'])
def get_history():
    """Get chat history for a user"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        if user_id not in chat_sessions:
            return jsonify({
                'success': True,
                'user_id': user_id,
                'history': [],
                'message': 'No chat history found'
            })
        
        chat_session = chat_sessions[user_id]['chat']
        history = []
        
        for msg in chat_session.history:
            history.append({
                'role': msg.role,
                'content': msg.parts[0].text if msg.parts else ''
            })
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'history': history
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/chat/reset', methods=['POST'])
def reset_chat():
    """Reset chat history for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        
        if user_id in chat_sessions:
            del chat_sessions[user_id]
        
        return jsonify({
            'success': True,
            'message': f'Chat history reset for user: {user_id}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(chat_sessions)
    })

if __name__ == '__main__':
    # Set your Gemini API key as environment variable:
    # export GEMINI_API_KEY="your_api_key_here"
    app.run(debug=True, host='0.0.0.0', port=5000)