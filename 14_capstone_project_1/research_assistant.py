import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv

# LangGraph & MySQL Persistence
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_community.tools import DuckDuckGoSearchRun

# LangChain & Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool

from operator import add as add_messages

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    research_count: int

#TOOL to save notes
@tool
def save_research_note(content:str, filename: str="research_notes.md") -> str:
    """
    Saves sysnthesized research content into a .md file.
    use this tool whenever you have finished summarizing a topic.
    """
    with open(filename,"a")as f:
        f.write(f"\n\n---Research Entry---\n{content}\n")
    return f"Successfully saved to {filename}"


search_tool = DuckDuckGoSearchRun()
tools=[search_tool, save_research_note]
tool_node=ToolNode(tools=tools)

model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview",
 api_key=api_key).bind_tools(tools)

#NODES
def call_model(state: AgentState):
    response = model.invoke(state["messages"])
    return {"messages": [response], "iterations": state.get("iterations", 0) + 1}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    
    # If the LLM didn't call a tool, it's done or giving its final answer
    if not last_message.tool_calls:
        return "done"
    if state.get("research_count",0)>=5:
        return "done"

        
    return "tools"

#GRAPH SETUP
app = StateGraph(AgentState)
app.add_node("agent",call_model)
app.add_node("action",tool_node)
app.set_entry_point("agent")

app.add_conditional_edges(
"agent", 
should_continue, 
{"tools": "action", 
"done": END})

app.add_edge("action","agent")

DB_URI=os.getenv("MYSQL_URL")
with PyMySQLSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()
    workflow = app.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "research_assistant_v2"}}
    inputs = {"messages": [HumanMessage(content="Research 2026 Stock market news")]}
    
    for event in workflow.stream(inputs, config=config, stream_mode="values"):
        event["messages"][-1].pretty_print()