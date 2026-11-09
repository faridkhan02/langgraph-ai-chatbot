
import streamlit as st

st.title("AI Chatbot")

st.write("Streamlit is working!")

user_input = st.chat_input("Type something...")

if user_input:
    st.write("You entered:", user_input)
