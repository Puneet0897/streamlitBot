import streamlit as st
from backend import get_response

# Streamlit UI Setup
st.set_page_config(page_title="Azure AI Chatbot", page_icon="💬", layout="wide")

st.title("💬 Azure AI-Powered Chatbot")
st.write("Ask me anything! I'll use Azure AI & Search to find the best answers.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat input box
user_input = st.text_input("Type your message:", key="user_input")

if user_input:
    response = get_response(user_input)
    st.session_state.chat_history.append(("User", user_input))
    st.session_state.chat_history.append(("Bot", response))

# Display chat history
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(text)

# Reset button
if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()
