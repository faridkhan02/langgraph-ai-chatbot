
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
import os

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq LLM
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    temperature=0.2
)

# Define chatbot state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Define chatbot node
def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# Create checkpointer
checkpointer = InMemorySaver()

# Create graph
graph = StateGraph(ChatState)

# Add node
graph.add_node("chat_node", chat_node)

# Add edges
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

# Compile graph
chatbot = graph.compile(checkpointer=checkpointer)
