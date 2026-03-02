import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from operator import add

load_dotenv()
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
    if state.get("iterations", 0) > 5:
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

def running_agent():
    print("--- STARTING AGENT ---")
    query = "Write a python script that calculates the 10th Fibonacci number but intentionaly start with an error in the logic first, then fix it."
    inputs = {"messages": [HumanMessage(content=query)], "iterations": 0}
    for output in app.stream(inputs):
        for key, value in output.items():
            if key == "call_model":
                msg = value["messages"][-1]
                if msg.tool_calls:
                    print(f"\n[Agent]: I'm writing/fixing code...")
                else:
                    print(f"\n[Final Answer]: {msg.content}")
            elif key == "tools":    
                print(f"[Tool Output]: {value['messages'][-1].content}")
if __name__ == "__main__":
    running_agent()