import streamlit as st
import requests

# ---------------- CONFIG ----------------
FASTAPI_URL = "http://localhost:8000/answer"  # FastAPI backend endpoint
st.set_page_config(page_title="Chat with FastAPI", page_icon="💬", layout="centered")

# ---------------- INITIALIZE SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []  # chat history

# ---------------- HEADER ----------------
st.title("💬 Datasmith AI Assignment")

# ---------------- SHOW CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- CHAT LOOP ----------------
# The loop runs on each new user input
if user_input := st.chat_input("Type your message..."):
    # 1️⃣ Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2️⃣ Send to FastAPI backend
    try:
        response = requests.post(FASTAPI_URL, data={"user_input": user_input, "session_id": "111"})
        response.raise_for_status()
        data = response.json()
        assistant_reply = data.get("result", "⚠️ No response received.")
        assistant_reply = assistant_reply[0].get("value")
    except Exception as e: 
        assistant_reply = f"❌ Error contacting backend: {e}"

    # 3️⃣ Add backend reply to state and display
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

# ---------------- NOTES ----------------
# st.markdown(
#     """
#     ---
#     **Tips:**
#     - Type a message and press Enter to send.
#     - The conversation persists in memory until you refresh the page.
#     - Connect to your FastAPI `/answer` endpoint that returns a JSON: `{"response": "..."}`
#     """
# )
