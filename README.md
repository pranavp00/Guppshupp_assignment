# Guppshupp_assignment
# 💬 AI Chatbot - Older Brother "Aarav"

A conversational AI chatbot that acts as your caring older brother, maintaining context across conversations and responding in Hindi, English, or Hinglish.

## 🎯 Features

✅ **Memory-based conversations** - Remembers previous chats  
✅ **Multi-language support** - Hindi, English, Hinglish  
✅ **Human-like responses** - 5-10 words, casual, with emojis  
✅ **Persona-driven** - Acts as caring older brother "Aarav"  
✅ **Context-aware** - Maintains conversation flow  
✅ **Emotional tone** - Friendly, caring, romantic, protective  

---

## 📁 Project Structure

```
project/
│
├── backend.py              # Flask API backend
├── streamlit_app.py        # Streamlit frontend
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
└── README.md              # This file
```

---

## 🚀 Setup Instructions

### 1. Clone/Download the Repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Gemini API Key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get your API key:**
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create/login to your account
- Generate an API key
- Copy and paste it in `.env`

### 4. Run the Backend

```bash
python backend.py
```

Backend will start on `http://localhost:5000`

### 5. Run the Frontend (New Terminal)

```bash
streamlit run streamlit_app.py
```

Frontend will open in your browser at `http://localhost:8501`

---

## 🧪 Testing the API

### Using cURL

**Send a message:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hey bro!", "user_id": "test_user"}'
```

**Get chat history:**
```bash
curl http://localhost:5000/chat/history?user_id=test_user
```

**Reset chat:**
```bash
curl -X POST http://localhost:5000/chat/reset \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:5000/chat",
    json={"message": "Bhai kya kar rahe ho?", "user_id": "my_user"}
)
print(response.json())
```

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send message and get response |
| GET | `/chat/history` | Get chat history for user |
| POST | `/chat/reset` | Reset chat history |
| GET | `/health` | Health check |

---

## 🎨 Conversation Examples

**English:**
```
User: "Hey bro, what's up?"
Aarav: "Nothing much 😊 what about you?"
```

**Hindi:**
```
User: "भाई, क्या कर रहे हो?"
Aarav: "बस आराम कर रहा हूं 😌 तुम बताओ?"
```

**Hinglish:**
```
User: "Yaar, bahut boring day hai"
Aarav: "Same yaar 😅 movie dekhein?"
```

---

## 🛠️ Tech Stack

- **Backend:** Flask + Google Gemini API
- **Frontend:** Streamlit
- **AI Model:** Gemini 2.5 Flash Lite
- **Language:** Python 3.8+

---

## 📦 Deployment

### Deploy Backend (Render/Railway)

1. Push code to GitHub
2. Connect to Render/Railway
3. Add environment variable: `GEMINI_API_KEY`
4. Deploy!

!

---

## 🤝 Assignment Requirements Compliance

| Requirement | Status |
|------------|--------|
| Backend API | ✅ Flask |
| AI Integration | ✅ Gemini |
| Memory/Context | ✅ Session-based |
| Persona | ✅ Older Brother "Aarav" |
| Response Length | ✅ 5-10 words |
| Incomplete Sentences | ✅ Natural flow |
| Human-like | ✅ Casual + emojis |
| Tone/Mood | ✅ Caring, friendly, romantic |
| Questions | ✅ Contextual follow-ups |
| Language Memory | ✅ Hindi/English/Hinglish |
| No Repetition | ✅ Contextual variety |

---

## 📧 Submission

**GitHub Repository:** Include:
- All source files (backend.py, streamlit_app.py)
- requirements.txt
- This README.md
- .env.example (sample env file)

**Demo Video:** (Optional but recommended)
- Record 2-3 minute demo showing conversations in different languages

---

## 👨‍💻 Author

Pranav Pillai  
ppillai294@gmail.com 


---

## 📄 License

MIT License - Feel free to use for educational purposes.

---

## 🐛 Troubleshooting

**Backend not starting?**
- Check if port 5000 is available
- Verify Gemini API key in `.env`

**Frontend not connecting?**
- Ensure backend is running first
- Check `API_URL` in streamlit_app.py

**API errors?**
- Verify internet connection
- Check Gemini API quota/limits

---

**Made with ❤️ for the AI Assignment**
