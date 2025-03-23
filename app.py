import streamlit as st
import requests

# Flask API URL
API_URL = "http://127.0.0.1:5000/chat"

# Streamlit UI
st.title("AI Chatbot")
st.markdown("### Ask your question below:")

# Initialize session state to store conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Function to send request to Flask backend
def ask_question(question):
    with st.spinner("Fetching response..."):
        response = requests.post(API_URL, json={"question": question})
        if response.status_code == 200:
            return response.json()
        else:
            return {"answer": "Error fetching response.", "follow-up questions": []}

# User input field
user_input = st.text_input("Enter your question:", key="user_input")

if st.button("Ask"):
    if user_input.strip():
        result = ask_question(user_input)
        st.session_state.conversation.append((user_input, result["answer"], result["follow-up questions"]))
    else:
        st.warning("Please enter a question.")

# Display conversation history
for idx, (question, answer, follow_ups) in enumerate(st.session_state.conversation):
    st.write(f"**You:** {question}")
    st.success(f"**AI:** {answer}")

    # Automatically handle follow-up questions
    for follow_up in follow_ups:
        if st.button(follow_up, key=f"followup_{idx}_{follow_up}"):
            result = ask_question(follow_up)
            st.session_state.conversation.append((follow_up, result["answer"], result["follow-up questions"]))
            st.experimental_rerun()  # Refresh the app to show new response
