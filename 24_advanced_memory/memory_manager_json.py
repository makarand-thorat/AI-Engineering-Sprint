import os
import json
from typing import Annotated, TypedDict, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# --- 1. Define the Memory Structure ---
class UserProfile(BaseModel):
    name: str = Field(default="Unknown", description="User's name")
    interests: List[str] = Field(default_factory=list, description="List of topics the user likes")
    location: str = Field(default="Unknown", description="Where the user is located")
    restrictions: List[str] = Field(default_factory=list, description="Things the user dislikes or avoids")


class State(TypedDict):
    messages: Annotated[list, add_messages]
    profile: dict 

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    api_key=os.getenv("GEMINI_API_KEY")
    )



def memory_node(state: State):
    """The 'Database Manager' Node: Extracts facts into a structured JSON."""
    current_profile = state.get("profile", UserProfile().model_dump())
    last_msg = state["messages"][-1].content
    
    # Tool-calling or direct structured output extraction
    structured_llm = llm.with_structured_output(UserProfile)
    
    prompt = f"""
    Current Profile: {json.dumps(current_profile)}
    New Message: {last_msg}
    
    Update the profile based on the new message. 
    If information is missing, keep the current values. 
    If new interests or restrictions are mentioned, add them to the list.
    """
    
    updated_profile_obj = structured_llm.invoke(prompt)
    return {"profile": updated_profile_obj.model_dump()}

def agent_node(state: State):
    """The Personalized Agent: Acts based on the structured JSON."""
    profile = state.get("profile", {})
    
    context_note = (
        f"You are talking to {profile['name']} in {profile['location']}. "
        f"They love {', '.join(profile['interests'])} but dislike {', '.join(profile['restrictions'])}."
    )
    
    system_msg = SystemMessage(content=f"Personalized Instructions: {context_note}")
    
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}


builder = StateGraph(State)
builder.add_node("memory", memory_node)
builder.add_node("agent", agent_node)

builder.add_edge(START, "memory")
builder.add_edge("memory", "agent")
builder.add_edge("agent", END)

graph = builder.compile(checkpointer=InMemorySaver())


config = {"configurable": {"thread_id": "json_memory_test"}}

print("--- Step 1: Storing Structured Data ---")
input_1 = "I'm Mak from NYC. I'm obsessed with rock climbing but I can't stand loud music."
for event in graph.stream({"messages": [HumanMessage(content=input_1)]}, config):
    if "memory" in event:
        print(f"PROFILE UPDATED: {event['memory']['profile']}")

print("\n--- Step 2: Querying with Context ---")
input_2 = "Can you suggest a weekend activity for me?"
for event in graph.stream({"messages": [HumanMessage(content=input_2)]}, config):
    if "agent" in event:
        print(f" AGENT: {event['agent']['messages'][0].content[0].get("text","")}")