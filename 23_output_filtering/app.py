import os
from typing import Annotated, TypedDict, Union, Literal, List
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

load_dotenv()

@tool
def post_to_social_media(content: str):
    """Posts content to social media. Only call this after human approval."""
    
    return f"Successfully posted: {content}"

def output_guardrail(state_content : str) -> bool:
    banned_words = ["crypto-scam", "spam", "buy-now-fast", "buy now!"]
    return not any(word in state_content.lower() for word in banned_words)

class State(TypedDict):
    messages : Annotated[List, add_messages]
    approved : bool


llm = ChatGoogleGenerativeAI(
    model= "gemini-3-flash-preview",
    api_key = os.getenv("GEMINI_API_KEY")
).bind_tools([post_to_social_media])


def agent_node(state: State):
    """The 'Brain' node that decides to research or post."""
    # Add a system instruction if the history is empty
    messages = state["messages"]
    if len(messages) == 1: # Only the user's first message is present
        system_instruction = HumanMessage(
            content="You are a social media assistant. Always use the 'post_to_social_media' tool when asked to share or post content."
        )
        messages = [system_instruction] + messages

    response = llm.invoke(messages)
    return {"messages" : [response]}

def human_approval_node(state: State):
    """
    The 'Checkpoint' node. It interrupts execution and waits for a 
    Command(resume=...) signal from the terminal/UI.
    """
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]
    proposed_content = tool_call['args'].get('content', '')

    if not output_guardrail(proposed_content):
        print("\n❌ GUARDRAIL TRIGGERED: Banned content detected!")
        return {
            "messages": [HumanMessage(content="Guardrail blocked this post due to banned words. Rewrite it.")],
            "approved": False
        }

    #interrupt if tool call is made
    print(f"\n--- 🛡️ PROPOSED POST ---\n{proposed_content}\n-----------------------")
    approval_response = interrupt(
        f"Agent wants to call tool: {last_message}. proceed? (yes/no)"
    )

    if approval_response.lower() == "yes":
        return {"approved" : True}
    else:
        return {
            "messages" : [HumanMessage(content="Action rejected by human. Please revise.")],
            "approved" : False
        }
    

def tool_node(state: State):
    """Execute only if approved flag is true"""
    if not state.get("approved"):
        return{"messages" : [HumanMessage(content="Tool execution blocked by guardrail.")]}
    
    #Demo tool call
    last_msg = state["messages"][-1]
    if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
        print("⚠️ Warning: tool_node called but no tool_calls found.")
        return {"messages": [HumanMessage(content="Error: No tool calls found.")]}

    tool_call =last_msg.tool_calls[0]
    result = post_to_social_media.invoke(tool_call["args"])

    return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}

def route_after_agent(state: State) -> Literal["human_approval", "end"]:
    """
    Check if the last message contains tool calls. 
    """
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "human_approval"
    return "end"

builder = StateGraph(State)

builder.add_node("agent" , agent_node)
builder.add_node("human_approval" , human_approval_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")


builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "human_approval": "human_approval",
        "end": END  
    }
)


#incase rejected
builder.add_conditional_edges(
    "human_approval",
    lambda state: "tools" if state["approved"] else "agent"
)
builder.add_edge("tools", "agent")

memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "day_23_session"}}
    print("Agent: Ready! Ask me to post something.")
    user_input = input("YOU: ")

    events = graph.stream({"messages": [HumanMessage(content=user_input)]}, config)

    for event in events:
        if "__interrupt__" in event:
            print(f"\n [INTERRUPT]:{event['__interrupt__'][0].value}")

            choice = input("your Decision (yes/no): ")
            graph.invoke(Command(resume = choice),config)
            break


        if "agent" in event:
            print(f"Agent thinking....")