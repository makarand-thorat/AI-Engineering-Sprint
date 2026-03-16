import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: str

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    api_key=os.getenv("GEMINI_API_KEY")
    )

def memory_node(state: State):
    current_memory = state.get("user_info", "No previous info.")
    last_user_msg = state["messages"][-1].content
    
   
    extraction_prompt = f"""
    Current Memory: {current_memory}
    New Message: {last_user_msg}
    
    Update the 'Current Memory' with any new permanent facts about the user from the 'New Message'.
    Include things like name, preferences, location, or goals. 
    Keep it concise. If no new info is found, just repeat the 'Current Memory'.
    """
    
    updated_memory = llm.invoke([HumanMessage(content=extraction_prompt)]).content
    return {"user_info": updated_memory}

def agent_node(state: State):
    user_profile = state.get("user_info", "a new user")
    
    system_msg = SystemMessage(content=f"""
    You are a helpful assistant. 
    Here is what you remember about the user: {user_profile}
    Use this info to personalize your response.
    """)
    
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}


builder = StateGraph(State)
builder.add_node("memory", memory_node)
builder.add_node("agent", agent_node)

builder.add_edge(START, "memory")
builder.add_edge("memory", "agent")
builder.add_edge("agent", END)

graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "smart_memory_001"}}

print("--- Round 1: Casual Intro ---")
msg1 = "Hey! I'm Gemini, I live in London and I'm a big fan of spicy food."
for event in graph.stream({"messages": [HumanMessage(content=msg1)]}, config):
    if "agent" in event:
        print(f"AGENT: {event['agent']['messages'][0].content[0].get("text","")}")

print("\n--- Round 2: Testing Memory ---")
msg2 = "I'm hungry, what should I get for dinner tonight?"
for event in graph.stream({"messages": [HumanMessage(content=msg2)]}, config):
    if "agent" in event:
        print(f"AGENT: {event['agent']['messages'][0].content[0].get("text","")}")