
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

st.title("AI Chatbot")

# Initialize chat history
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# Display previous messages
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

config = {
    "configurable": {
        "thread_id": "1"
    }
}

# Get user input
user_input = st.chat_input("Type here...")

if user_input:

    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.text(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chatbot.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )

            ai_message = response["messages"][-1].content
            st.text(ai_message)

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })
