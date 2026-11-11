# LangGraph AI Chatbot

A tool-enabled conversational AI chatbot built with **LangGraph**,
**Groq**, **LangChain**, **Streamlit**, and **SQLite**. It supports
streaming assistant responses, multiple chat threads, persistent
conversation checkpoints, and tool calling for web search, stock quotes,
and calculations.

## Highlights

-   **Streaming chat:** Assistant output is rendered token-by-token with
    Streamlit's `st.write_stream`.
-   **LangGraph workflow:** Uses a `StateGraph` with a chatbot node, a
    tool node, conditional routing, and a loop back to the chatbot after
    tool execution.
-   **Groq-powered LLM:** Connects to the Groq API using LangChain's
    `ChatGroq` integration and the `openai/gpt-oss-120b` model.
-   **Tool calling:** The model can call:
    -   DuckDuckGo/Bing-backed web search.
    -   An Alpha Vantage stock-quote function.
    -   A calculator supporting addition, subtraction, multiplication,
        and division.
-   **SQLite checkpointing:** Uses LangGraph's `SqliteSaver` to persist
    graph state for conversations.
-   **Multiple conversations:** The Streamlit sidebar lets users start a
    new chat and switch between conversation threads.
-   **Conversation history:** Messages are stored in LangGraph state and
    loaded when a thread is selected.

## Tech Stack

  -----------------------------------------------------------------------
  Technology                          How it is used
  ----------------------------------- -----------------------------------
  Python                              Main application language

  LangGraph                           Stateful chatbot workflow, routing,
                                      and checkpointing

  LangChain                           Message types, tool definitions,
                                      and model integration

  Groq                                LLM API provider

  `ChatGroq`                          Connects the application to the
                                      Groq-hosted model

  Streamlit                           Interactive chat UI and streamed
                                      output

  SQLite                              Persistent LangGraph checkpoints

  DuckDuckGo Search                   Search tool integration (configured
                                      with the `bing` backend)

  Alpha Vantage                       Stock quote data API

  `python-dotenv`                     Loads environment variables from
                                      `.env`

  `requests`                          Makes the stock quote API request
  -----------------------------------------------------------------------

## Architecture

``` text
User
 |
 v
Streamlit Chat UI
 |
 | user message + thread_id
 v
LangGraph StateGraph
 |
 v
Chat Node (Groq LLM with bound tools)
 |
 +---- normal assistant response ----> Streamlit streaming output
 |
 +---- tool call requested
          |
          v
       ToolNode
          |
          +---- Web Search
          +---- Stock Quote
          +---- Calculator
          |
          v
       Chat Node
          |
          v
       Assistant response

LangGraph Checkpointer <----> SQLite database
```

### Request flow

1.  The user enters a message in the Streamlit chat input.
2.  The frontend sends a `HumanMessage` to the graph with the current
    `thread_id`.
3.  The chatbot node invokes the Groq model with the available tools
    bound to it.
4.  LangGraph checks whether the model requested a tool call.
5.  If a tool is requested, `ToolNode` executes it and sends the result
    back to the chatbot node.
6.  The model produces its final response.
7.  The frontend consumes `chatbot.stream(..., stream_mode="messages")`
    and displays assistant message chunks using `st.write_stream`.
8.  The SQLite checkpointer saves the graph checkpoint under that
    conversation's thread ID.

## Available Tools

### 1. Web search

The project creates a `DuckDuckGoSearchRun` tool using
`DuckDuckGoSearchAPIWrapper`. The wrapper is configured with:

-   Region: `us-en`
-   Maximum results: `5`
-   Backend: `bing`

The search tool can retrieve web information in response to questions
when the model chooses to call it.

### 2. Stock quote

The `get_stock_price(symbol)` tool sends a request to Alpha Vantage's
`GLOBAL_QUOTE` endpoint and returns the JSON response.

Example symbols in the code comments include `AAPL` and `TSLA`.
Availability and returned data depend on the API provider, symbol
format, and API limits.

**Security note:** Do not put an Alpha Vantage API key directly in
Python source code. The uploaded backend contains a hard-coded key in
the request URL. Remove it from the source, move it to an environment
variable, and rotate/regenerate that key because it has been exposed in
source code.

Recommended pattern:

``` python
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

url = "https://www.alphavantage.co/query"
params = {
    "function": "GLOBAL_QUOTE",
    "symbol": symbol,
    "apikey": ALPHA_VANTAGE_API_KEY,
}
response = requests.get(url, params=params, timeout=15)
response.raise_for_status()
return response.json()
```

### 3. Calculator

The `calculator(first_num, second_num, operation)` tool supports:

  Operation        Value to pass
  ---------------- ---------------
  Addition         `add`
  Subtraction      `sub`
  Multiplication   `mul`
  Division         `div`

The tool returns the calculation result and handles division by zero and
unsupported operations.

## Project Structure

Based on the two uploaded source files, the core application consists
of:

``` text
LANGGRAPH-CHATBOT/
|
├── langgraph_backend.py
├── streaming_frontend_threading.py
├── .env
├── .gitignore
└── chatbot.db
```

The backend source uploaded for this README was named
`langgraph_tool_backend.py`, while the frontend imports `chatbot` from
`langgraph_backend`. Make sure the actual backend filename and the
import statement match. For the structure above, either rename the
backend file to `langgraph_backend.py` or update the frontend import to
the actual module name.

Other local files, virtual environments, and database sidecar files are
not included in this core structure.

## Setup and Installation

### Prerequisites

-   Python 3.10 or newer
-   A Groq API key
-   An Alpha Vantage API key for the stock quote tool
-   Internet access for the LLM and search/stock tools

### 1. Clone the repository

Replace the placeholders with your GitHub username and repository name:

``` bash
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>
```

### 2. Create a virtual environment

**Windows PowerShell**

``` powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

**macOS/Linux**

``` bash
python -m venv myenv
source myenv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -U streamlit langgraph langchain langchain-core langchain-groq langgraph-checkpoint-sqlite langchain-community duckduckgo-search python-dotenv requests
```

If your installed LangChain/LangGraph versions require a different
search integration package, follow the package's current installation
instructions.

### 4. Configure environment variables

Create a `.env` file in the project root:

``` env
GROQ_API_KEY=your_groq_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
```

Never commit `.env` or publish API keys in screenshots, source code, or
logs.

### 5. Run the app

The uploaded frontend file is named `streaming_frontend_threading.py`.
Run:

``` powershell
streamlit run streaming_frontend_threading.py
```

Streamlit will display a local URL, typically:

``` text
http://localhost:8501
```

Open the URL in your browser to use the chatbot.

## Conversation Memory and SQLite

The backend creates a SQLite connection to `chatbot.db` and uses
LangGraph's `SqliteSaver` as the graph checkpointer.

Each conversation is identified by a UUID thread ID. The frontend passes
the selected thread ID as:

``` python
CONFIG = {
    "configurable": {
        "thread_id": st.session_state["thread_id"]
    }
}
```

When a conversation is selected, the frontend calls
`chatbot.get_state(...)` to load the saved graph messages.

**Current implementation detail:** The graph checkpoints are stored in
SQLite, but the sidebar's `chat_threads` list is held in Streamlit
session state. The uploaded code does not persist that thread list
separately. Consequently, checkpoint data may remain in the database
even if the sidebar list is reset when the app session restarts.

## Streaming Implementation

The frontend uses LangGraph's message streaming mode and Streamlit's
stream renderer:

``` python
for message_chunk, metadata in chatbot.stream(
    {"messages": [HumanMessage(content=user_input)]},
    config=CONFIG,
    stream_mode="messages",
):
    if isinstance(message_chunk, AIMessage):
        yield message_chunk.content
```

`st.write_stream()` renders the yielded assistant content incrementally
in the chat window.

## Security and Git Hygiene

Before publishing the repository:

-   Remove the hard-coded Alpha Vantage key from the backend.
-   Rotate the exposed Alpha Vantage key and store the replacement in
    `.env`.
-   Keep `.env` out of Git.
-   Do not commit your virtual environment.
-   Decide whether the local SQLite database should be private or
    excluded from the repository.
-   Avoid committing SQLite write-ahead log and shared-memory files.

Suggested `.gitignore`:

``` gitignore
# Secrets
.env
.streamlit/secrets.toml

# Virtual environments
myenv/
.venv/
venv/

# Python generated files
__pycache__/
*.py[cod]

# Local databases
chatbot.db
chatbot.db-shm
chatbot.db-wal

# Editor and OS files
.vscode/
.DS_Store
```

## Possible Improvements

-   Persist the conversation/thread list so previous chats remain
    discoverable after a restart.
-   Add a delete-conversation option.
-   Add error handling and timeouts for external API requests.
-   Validate stock symbols and handle Alpha Vantage rate-limit or error
    responses.
-   Add tests for calculator operations, tool routing, thread
    persistence, and streaming.
-   Add authentication and isolate conversations between users before
    deploying publicly.
-   Add deployment configuration and manage API keys through the hosting
    platform's secrets manager.

## Author

**Farid Khan**

-   GitHub: [faridkhan02](https://github.com/faridkhan02)
-   LinkedIn: [Md Farid
    Khan](https://www.linkedin.com/in/md-farid-khan-bb662b2b4/)

------------------------------------------------------------------------

If you find this project useful, consider giving the repository a ⭐.
