import streamlit as st
import requests  # type: ignore
import os

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000/api/chat")

st.set_page_config(page_title="InfluxDB RAG Chat", layout="centered")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "show_thinking" not in st.session_state:
    st.session_state.show_thinking = False

st.title("InfluxDB RAG Assistant")

# Display chat history
with st.container():
    for sender, msg in st.session_state.chat_history:
        with st.chat_message(sender):
            st.markdown(msg)

    # Show placeholder while processing
    if st.session_state.show_thinking:
        with st.chat_message("assistant"):
            st.markdown("Thinking...")

# Handle input
if user_question := st.chat_input("Ask a question..."):
    st.session_state.chat_history.append(("user", user_question))
    st.session_state.pending_question = user_question
    st.session_state.show_thinking = True
    st.rerun()  # Triggers the "Thinking..." phase

# Handle response fetch
if st.session_state.pending_question and st.session_state.show_thinking:
    try:
        res = requests.post(
            API_ENDPOINT,
            json={"question": st.session_state.pending_question},
        )
        answer = res.json().get("answer", "No answer.")
    except Exception as e:
        answer = f"Error: {e}"

    st.session_state.chat_history.append(("assistant", answer))
    st.session_state.pending_question = None
    st.session_state.show_thinking = False
    st.rerun()  # Replace "Thinking..." with the real answer
