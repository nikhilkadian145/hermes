import requests
import json
import time

try:
    print("Health check:", requests.get("http://localhost:5000/api/health").json())
    
    # 1. Start a new text to agent
    res = requests.post("http://localhost:5000/api/chat/message", json={
        "message": "Hello HERMES. What's my outstanding balance?",
    })
    data = res.json()
    print("Post msg:", data)
    
    conversation_id = data["conversation_id"]
    
    # 2. Poll for 20 seconds
    for _ in range(10):
        time.sleep(2)
        poll_res = requests.get(f"http://localhost:5000/api/chat/poll/{conversation_id}?after=0")
        poll_data = poll_res.json()
        if poll_data.get("has_new"):
            print("Received response:", json.dumps(poll_data["messages"], indent=2))
            break
        else:
            print("No response yet...")
except Exception as e:
    print("Error:", e)
