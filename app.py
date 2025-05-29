import streamlit as st
import requests

API_URL = "http://localhost:8000/chat"  # Point this to your backend

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by an AI Agent")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

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
                response = requests.post(API_URL, json={"messages": st.session_state["messages"]})
                response.raise_for_status()
                reply = response.json()["response"]
            except Exception as e:
                reply = f"Error: {e}"
            st.session_state["messages"].append({"role": "assistant", "content": reply})
            st.write(reply)

