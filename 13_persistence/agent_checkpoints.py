import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv

# LangGraph & MySQL Persistence
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# LangChain & Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from operator import add

load_dotenv()
DB_URI = os.getenv("MYSQL_URL")
if not DB_URI:
    raise ValueError("MYSQL_URL not found in .env file! Check your credentials.")

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", # Highly capable at coding
    temperature=0,             # Keep it precise for debugging
    api_key=os.getenv("GEMINI_API_KEY")
)


@tool
def python_executor(code: str) -> str:
    """
    Execute python code and return the output or error.
    Input should be pure python code string.
    """
    import sys
    from io import StringIO

    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()

    try:
        exec(code, {})
        sys.stdout = old_stdout
        return redirected_output.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        return f"EXECUTION ERROR: {e}"


tools = [python_executor]
llm_with_tools = llm.bind_tools(tools)


class AgentState(TypedDict):
    # We use add to keep the history so the LLM can see the previous error
    messages: Annotated[Sequence[BaseMessage], add]
    iterations: int

def call_model(state: AgentState):
    system_prompt = (
        "You are a Python Coding Expert. Your goal is to write code to solve user requests. "
        "IMPORTANT: If the 'python_executor' returns an 'EXECUTION_ERROR', do not give up. "
        "Analyze the error, explain why it happened, and write a corrected version of the code. "
        "Always use the tool to verify your fix."
    )
    
    # Injecting the system prompt at the start of the message list
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    # We increment iterations to prevent infinite loops
    return {"messages": [response], "iterations": state.get("iterations", 0) + 1}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    
    # If the LLM didn't call a tool, it's done or giving its final answer
    if not last_message.tool_calls:
        return "done"
    
    # Limit to 5 attempts to fix the bug
    if state.get("iterations", 0) > 3:
        print("--- MAX ITERATIONS REACHED ---")
        return "done"
        
    return "tools"

graph = StateGraph(AgentState)
graph.add_node("call_model", call_model)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("call_model")
graph.add_conditional_edges(
    "call_model",
    should_continue,
    {
        "done" : END,
        "tools": "tools"
    }

)
graph.add_edge("tools", "call_model")
app = graph.compile()

with PyMySQLSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()
    app=graph.compile(checkpointer=checkpointer)
    config ={"configurable":{"thread_id":"user_session_001"}}

    print("--- STARTING AGENT ---")
    initial_input={"messages":[HumanMessage(content="Write a script to calculate 50 factorial")]}
    for output in app.stream(initial_input, config=config,stream_mode="updates"):
        for node,value in output.items():
            if node == "call_model":
                last_message = value["messages"][-1]
                if last_message.content:
                    print(f"Agent: {last_message.text}")
            elif  node == "tools":
                print(f"Tool Results: {value['messages'][-1].content}")