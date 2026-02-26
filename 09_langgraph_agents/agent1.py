from typing import TypedDict,List,Union
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,AIMessage
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key=os.getenv("GEMINI_API_KEY"),
    
)
class AgentState(TypedDict):
    messages: List[Union[HumanMessage,AIMessage]]

def process(state: AgentState)-> AgentState:
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print(f"\nAI: {response.text}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process",process)
graph.add_edge(START,"process")
graph.add_edge("process",END)
agent=graph.compile()

chat_history=[]
user_input = input("Enter: ")
while user_input !="exit":
    chat_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": chat_history})
    chat_history=result["messages"]
    user_input = input("Enter: ")

