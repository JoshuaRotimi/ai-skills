import streamlit as st
import requests
import json

API_URL = "https://kya-risk-agent.onrender.com/api/transaction/chat"

st.title("💬 KYC Risk Assessment - Chatbot")
st.caption("🚀 A RIsk Assessment AI agent powered by an Microsoft Semantic Kernel")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Debug section
with st.expander("Debug Info"):
    st.write("API URL:", API_URL)
    st.write("Current messages:", st.session_state["messages"])

# Render messages
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
if prompt := st.chat_input():
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Extract just the latest user message
                latest_user_message = None
                for msg in reversed(st.session_state["messages"]):
                    if msg["role"] == "user":
                        latest_user_message = msg["content"]
                        break
                
                # Try different payload formats based on common backend expectations
                payload_options = [
                    {"message": latest_user_message},  # Most common
                    {"prompt": latest_user_message},   # Alternative
                    {"content": latest_user_message},  # Another alternative
                    {"messages": st.session_state["messages"]},  # Your current format
                ]
                
                # Start with the most likely format
                payload = payload_options[0]
                
                # Make the request with more detailed error handling
                response = requests.post(
                    API_URL, 
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30  # Add timeout
                )
                
                
                if response.status_code == 200:
                    response_data = response.json()
                    # st.write("DEBUG - Full response:", response_data)
                    
                    # Try different possible response keys
                    if "response" in response_data:
                        reply = response_data["response"]
                    elif "message" in response_data:
                        reply = response_data["message"]
                    elif "reply" in response_data:
                        reply = response_data["reply"]
                    else:
                        reply = f"Unexpected response format: {response_data}"
                else:
                    reply = f"HTTP Error {response.status_code}: {response.text}"
                    
            except requests.exceptions.Timeout:
                reply = "Error: Request timed out. Backend may be slow or unresponsive."
            except requests.exceptions.ConnectionError:
                reply = "Error: Could not connect to backend. Check if the URL is correct and backend is running."
            except requests.exceptions.HTTPError as e:
                reply = f"HTTP Error: {e}"
            except json.JSONDecodeError:
                reply = f"Error: Backend returned invalid JSON. Response: {response.text}"
            except Exception as e:
                reply = f"Unexpected error: {type(e).__name__}: {e}"
            
            st.session_state["messages"].append({"role": "assistant", "content": reply})
            st.write(reply)
