from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from datetime import datetime
import sqlite3
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# In-RAM chat sessions (Gemini chat objects)
chat_sessions = {}

# -----------------------------
# ✅ SQLite Persistent Memory
# -----------------------------
DB_PATH = "memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message_to_db(user_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO memory (user_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def load_memory_from_db(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT role, content FROM memory
        WHERE user_id=?
        ORDER BY id ASC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

# -----------------------------
# Your Original System Prompt
# -----------------------------
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

# -----------------------------
# Gemini Chat Session Manager
# -----------------------------
def get_or_create_chat(user_id):
    """Get existing chat session or create new one"""
    if user_id not in chat_sessions:

        # Load past DB memory into Gemini history
        past_messages = load_memory_from_db(user_id)
        gemini_history = []
        for msg in past_messages:
            gemini_history.append(
                {"role": msg["role"], "parts": [msg["content"]]}
            )

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=system_instruction
        )

        chat_sessions[user_id] = {
            "chat": model.start_chat(history=gemini_history),
            "created_at": datetime.now().isoformat()
        }

    return chat_sessions[user_id]["chat"]

# -----------------------------
# /chat Endpoint (Unchanged + Memory Save)
# -----------------------------
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400

        user_message = data['message']
        user_id = data.get('user_id', 'default_user')

        # Save user message into persistent memory
        save_message_to_db(user_id, "user", user_message)

        # Load chat session
        chat_session = get_or_create_chat(user_id)

        # Get response
        response = chat_session.send_message(user_message)
        assistant_text = response.text

        # Save assistant reply into DB
        save_message_to_db(user_id, "assistant", assistant_text)

        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': user_message,
            'response': assistant_text,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# -----------------------------
# /chat/history Endpoint (unchanged + DB memory)
# -----------------------------
@app.route('/chat/history', methods=['GET'])
def get_history():
    try:
        user_id = request.args.get('user_id', 'default_user')

        history = load_memory_from_db(user_id)

        return jsonify({
            'success': True,
            'user_id': user_id,
            'history': history
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# -----------------------------
# /chat/reset Endpoint
# -----------------------------
@app.route('/chat/reset', methods=['POST'])
def reset_chat():
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')

        # Clear in-memory Gemini chat
        if user_id in chat_sessions:
            del chat_sessions[user_id]

        # Clear persistent memory
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM memory WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Chat history reset for user: {user_id}'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# -----------------------------
# /health Endpoint (unchanged)
# -----------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(chat_sessions)
    })

# -----------------------------
# App Start
# -----------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
