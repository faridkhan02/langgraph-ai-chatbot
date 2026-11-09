
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
        st.write(message["content"])

# LangGraph configuration
config = {
    "configurable": {
        "thread_id": "thread-1"
    }
}

# User input
user_input = st.chat_input("Type here...")

if user_input:

    # Display user message
    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    # Generate AI response
    with st.chat_message("assistant"):

        def generate_response():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages"
            ):
                content = message_chunk.content

                if isinstance(content, str) and content:
                    yield content

        ai_message = st.write_stream(generate_response())

    # Save assistant response
    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })
