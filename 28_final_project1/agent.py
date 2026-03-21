import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Annotated, TypedDict
from langchain_core.messages import ToolMessage,SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState

load_dotenv()
search_tool = DuckDuckGoSearchRun()

tools = [search_tool]
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key= os.getenv("GEMINI_API_KEY")
    ).bind_tools(tools)


def call_model(state):
    system_instruction = SystemMessage(content=(
        "You are a 'Company Researcher & Email Drafter'. "
        "Your workflow is: "
        "1. Search for the company's mission and recent news using DuckDuckGo. "
        "2. Analyze the findings. "
        "3. Draft a high-conversion, personalized partnership email. "
        "Always provide the research summary before the email draft."
    ))
    messages = [system_instruction] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def call_tool(state):
    last_message = state["messages"][-1]
    results = []

    for tool_call in last_message.tool_calls:
        print(f"🤖 LLM requested search: {tool_call['args']}")
        observation = search_tool.invoke(tool_call["args"])
        results.append(ToolMessage(
            tool_call_id=tool_call["id"],
            content=str(observation)
        ))

    return {"messages": results}

def should_continue(state):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "end"

workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tool)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools", 
        "end": END        
    }
)
workflow.add_edge("tools", "agent")
app = workflow.compile()