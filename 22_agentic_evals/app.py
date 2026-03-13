import os
from typing import Annotated, TypedDict, Union
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import wrappers

load_dotenv()
print(f"Is tracing actually on? {os.getenv('LANGSMITH_TRACING')}")
@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two integers. Use this for math."""
    return a * b

tools = [multiply]

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key=os.getenv("GEMINI_API_KEY")
    ).bind_tools(tools)
# client = wrappers.wrap_gemini(
#         llm,
#         tracing_extra={
#             "tags": ["gemini", "python"],
#             "metadata": {
#                 "integration": "google-genai",
#             },
#         },
#     )

class AgentState(TypedDict):
    
    messages: Annotated[list[BaseMessage], add_messages]


def call_model(state: AgentState):
    """The 'Brain' node: decides to use a tool or finish."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools)) 

workflow.add_edge(START, "agent")


workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools", 
        "__end__": END
    }
)

workflow.add_edge("tools", "agent") 

app = workflow.compile()


if __name__ == "__main__":
    print(f"🚀 Project: {os.getenv('LANGSMITH_PROJECT')}")
    
    inputs = {"messages": [HumanMessage(content="What is 15 times 15?")]}
    
    for chunk in app.stream(inputs, stream_mode="values"):
        if "messages" in chunk:
            chunk["messages"][-1].pretty_print()

