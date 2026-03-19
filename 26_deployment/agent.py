import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage,RemoveMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def call_model(state: AgentState):
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        api_key=os.getenv("GEMINI_API_KEY")
    )
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def create_agent():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    
    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)

def clear_thread_memory(thread_id: str):
    """
    Deletes all checkpoints for a specific thread_id.
    """
    # config for the checkpointer
    config = {"configurable": {"thread_id": thread_id}}
    current_state = graph.get_state(config)
    messages = current_state.values.get("messages", [])
    if messages:
        
        delete_commands = [RemoveMessage(id=m.id) for m in messages]
        graph.update_state(config, {"messages": delete_commands})
    return True


graph = create_agent()

if __name__ == "__main__":
    # Test message
    test_input = {"messages": [HumanMessage(content="Hello! Who are you?")]}
    config = {"configurable": {"thread_id": "test_123"}}
    
    print("Testing Agent Logic...")
    response = graph.invoke(test_input, config=config)
    print(f"Agent Response: {response['messages'][-1].content[0].get("text","")}")