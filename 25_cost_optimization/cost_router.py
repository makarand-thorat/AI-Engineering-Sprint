import os
from typing import Literal, TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph,START,END

load_dotenv()

small_llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key = os.getenv("GEMINI_API_KEY")
    )
large_llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key= os.getenv("GEMINI_API_KEY")
    )

class State(TypedDict):
    messages : list
    complexity : str

def router_node(state: State):
    last_msg = state["messages"][-1].content

    prompt = f"Classify this task as 'easy' (greeting, simple facts) or 'complex (reasoning, code, analysis): {last_msg} answer only a single word easy or complex"
    decision = small_llm.invoke(prompt).content.lower()
    print(f"THE DECISION is {decision}")
    complexity = "complex" if "complex" in decision else "easy"
    print(f"ROUTER: Detected {complexity.upper()} task.")
    return {"complexity" : complexity}

def small_model_node(state: State):
    print("Using Gemini Flash (Cost: $)")
    response = small_llm.invoke(state["messages"])
    return {"messages": [response]}

def large_model_node(state: State):
    print("Using Gemini Pro (Cost: $$$)")
    response = large_llm.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(State)

builder.add_node("router", router_node)
builder.add_node("small", small_model_node)
builder.add_node("large", large_model_node)

builder.add_edge(START, "router")
builder.add_conditional_edges(
    "router",
    lambda state: "small" if state["complexity"] == "easy" else "large"

)
builder.add_edge("small",END)
builder.add_edge("large",END)

builder.add_edge("small",END)

graph = builder.compile()
print("Test 1: 'Hi how are you?'")
final_state=graph.invoke({"messages": [HumanMessage(content="Hi how are you?")]})
print(final_state['messages'][-1].content)

print("\n-------------------------------------------")

print("\nTest 2: 'Write a Python script to scrape a website'")
final_state2=graph.invoke({"messages": [HumanMessage(content="Write a Python script to scrape a website")]})
print(final_state2['messages'][-1].content[0].get("text",""))