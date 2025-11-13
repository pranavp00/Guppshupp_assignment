import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:5000"  # Change this if backend is hosted elsewhere

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Page config
st.set_page_config(
    page_title="Chat with Aarav 💬",
    page_icon="👨‍👦",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("💬 Chat with Aarav")
st.markdown("*Your caring older brother*")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.info(f"**User ID:** `{st.session_state.user_id}`")
    
    if st.button("🔄 Reset Chat", use_container_width=True):
        try:
            response = requests.post(
                f"{API_URL}/chat/reset",
                json={"user_id": st.session_state.user_id}
            )
            if response.status_code == 200:
                st.session_state.messages = []
                st.success("Chat reset successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📝 Features")
    st.markdown("""
    - 🧠 Remembers conversations
    - 🌐 Multi-language (Hindi/English/Hinglish)
    - 😊 Friendly & caring tone
    - 💬 Human-like responses
    """)
    
    # Health check
    try:
        health = requests.get(f"{API_URL}/health")
        if health.status_code == 200:
            data = health.json()
            st.success(f"✅ Backend Connected")
            st.caption(f"Active sessions: {data.get('active_sessions', 0)}")
        else:
            st.error("❌ Backend Disconnected")
    except:
        st.error("❌ Backend Disconnected")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message... (Hindi, English, or Hinglish)"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Typing... ⏳")
        
        try:
            # Call backend API
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "message": prompt,
                    "user_id": st.session_state.user_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', 'Sorry, no response received.')
                
                # Display AI response
                message_placeholder.markdown(ai_response)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })
            else:
                error_msg = "❌ Error: Unable to get response"
                message_placeholder.markdown(error_msg)
                st.error(f"Status code: {response.status_code}")
        
        except requests.exceptions.Timeout:
            error_msg = "⏰ Request timed out. Please try again."
            message_placeholder.markdown(error_msg)
        
        except requests.exceptions.ConnectionError:
            error_msg = "❌ Cannot connect to backend. Make sure Flask server is running on port 5000."
            message_placeholder.markdown(error_msg)
        
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            message_placeholder.markdown(error_msg)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: white;'>"
    "Made By Pranav | Powered by Gemini AI"
    "</div>",
    unsafe_allow_html=True
)