import os
from typing import Annotated,List,TypedDict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from operator import add as add_messages

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Token Saver: Only keep the last 6 messages to prevent context bloat
def limit_messages(left: list, right: list):
    full_list = left + right
    return full_list[-6:]

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], limit_messages]
    next_agent: str

@tool
def web_search(query: str):
    """Search the web for the latest information."""
    return f"Results for {query}:[Simulated search data about AI 2026]"

@tool
def write_file(content: str, filename: str):
    """Write the final report to a local markdown file."""
    with open(filename, "w") as f:
        f.write(content)
    return f"File {filename} saved successfully."

llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview",
 api_key=api_key)

def supervisor(state: AgentState):

    """The Brain: Decides who works next."""
    prompt = """You are a Research Supervisor. 
    If the user asks a question, call 'researcher'.
    If the research is done, call 'writer' to save it.
    If the report is saved, respond with 'FINISH'."""
# Get the last entry in the message history
    last_entry = state["messages"][-1]
    
    # FIX: If the last entry is a list of ToolMessages, combine their text
    if isinstance(last_entry, list):
        last_msg_content = " ".join([m.content for m in last_entry]).lower()
    else:
        last_msg_content = last_entry.content.lower()
    if "saved" in last_msg_content:
        return {"next_agent": "FINISH"}
    elif "results" in last_msg_content:
        return {"next_agent": "writer"}
    return {"next_agent": "researcher"}

def researcher(state: AgentState):
    """Specialist: Gathers Data."""
    # FIX: Send only the very first message (User Query) and the very last one
    # This ensures a HumanMessage is always present for Gemini
    context = [state["messages"][0], state["messages"][-1]]
    response = llm.bind_tools([web_search]).invoke(context)
    return {"messages": [response]}

def writer(state: AgentState):
    """Specialist: Formats and saves data (Fixed for Gemini Turn-Order)."""
    print("--- WRITER WORKING ---")
    
    # 1. Get the research results
    raw_data = state["messages"][-1]
    
    # 2. Extract content (handle if it's a list or a message)
    if isinstance(raw_data, list):
        content = " ".join([m.content for m in raw_data])
    else:
        content = raw_data.content

    # 3. FORCE the turn order: System Role + Data wrapped in a HumanMessage
    # This satisfies Gemini's requirement for a "user turn" before a function call
    context = [
        HumanMessage(content=(
            f"You are a Technical Writer. Take the following research and use the "
            f"'write_file' tool to save it to report.md.\n\n"
            f"RESEARCH DATA: {content}"
        ))
    ]
    
    # 4. Invoke with tools
    response = llm.bind_tools([write_file]).invoke(context)
    return {"messages": [response]}
def router(state):
    if state["next_agent"] == "FINISH": return END
    return state["next_agent"]


workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor)
workflow.add_node("researcher", researcher)
workflow.add_node("writer", writer)
workflow.add_node("tools", ToolNode([web_search, write_file]))

workflow.set_entry_point("supervisor")


workflow.add_conditional_edges("supervisor", router)
workflow.add_edge("researcher", "tools")
workflow.add_edge("writer", "tools")
workflow.add_edge("tools", "supervisor")

app = workflow.compile()

for event in app.stream({"messages": [HumanMessage(content="Research 2026 tech trends and save to report.md")]}):
    print(event)