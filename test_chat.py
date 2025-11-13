import requests
import json

API_URL = "http://localhost:5000"

def chat(message, user_id="test_user"):
    """Send a chat message"""
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "message": message,
            "user_id": user_id
        }
    )
    return response.json()

def get_history(user_id="test_user"):
    """Get chat history"""
    response = requests.get(
        f"{API_URL}/chat/history",
        params={"user_id": user_id}
    )
    return response.json()

def reset_chat(user_id="test_user"):
    """Reset chat history"""
    response = requests.post(
        f"{API_URL}/chat/reset",
        json={"user_id": user_id}
    )
    return response.json()

# Simple interactive loop
if __name__ == "__main__":
    print("=== Aarav Chat Test Client ===")
    print("Commands: 'history', 'reset', 'exit'\n")
    
    user_id = input("Enter your user ID (press enter for 'test_user'): ").strip() or "test_user"
    
    while True:
        user_input = input(f"\n[{user_id}] You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Aarav: Take care bro ❤️, bye!")
            break
        
        elif user_input.lower() == "history":
            result = get_history(user_id)
            if result['success']:
                print("\n--- Chat History ---")
                for msg in result['history']:
                    print(f"{msg['role']}: {msg['content']}")
                print("--- End History ---")
            else:
                print(f"Error: {result.get('error')}")
        
        elif user_input.lower() == "reset":
            result = reset_chat(user_id)
            print(result.get('message', 'Reset successful'))
        
        else:
            result = chat(user_input, user_id)
            if result['success']:
                print(f"Aarav: {result['response']}")
            else:
                print(f"Error: {result.get('error')}")