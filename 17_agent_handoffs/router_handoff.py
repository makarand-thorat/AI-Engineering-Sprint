import os
from typing import Literal
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model = "gemini-3-flash-preview",
    api_key= os.getenv("GEMINI_API_KEY")
)

#ROUTERNODE

def router_node(state: MessagesState):
    prompt = "Is the following request a math problem or a creative writing task? Reply with only 'math' or 'creative'."
    decision = llm.invoke([HumanMessage(content=prompt + "\n\n" + state["messages"][-1].content)])
    print(decision.content[0]['text'].lower())
    if "math" in decision.content[0]['text'].lower():
        return Command(
            goto="math_expert",
            update={"messages":[AIMessage(content= "I'm transferring you to our Math Department.")]}
        )
    else:
        return Command(
            goto="creative_expert",
            update={"messages":[AIMessage(content= "Sending this to out creative Writing team.")]}
        )

def math_expert(state: MessagesState):
    print("--- MATH EXPERT WORKING ---")
    # We look at the very first message for the actual question
    original_question = state["messages"][0].content
    response = llm.invoke(f"Solve this math problem clearly and provide just the answer: {original_question}")
    return {"messages": [response]}

def creative_expert(state: MessagesState):
    print("--- CREATIVE EXPERT WORKING ---")
    original_question = state["messages"][0].content
    response = llm.invoke(f"Write a very short and beautiful response to: {original_question}")
    return {"messages": [response]}


workflow = StateGraph(MessagesState)
workflow.add_node("router", router_node)
workflow.add_node("math_expert", math_expert)
workflow.add_node("creative_expert", creative_expert)

workflow.add_edge(START, "router")
workflow.add_edge("math_expert", END)
workflow.add_edge("creative_expert", END)

app = workflow.compile()


if __name__ == "__main__":
    # Test 1: Math
    print("\n--- Test 1: Math ---")
    for event in app.stream({"messages": [HumanMessage(content="What is 15% of 450?")]}):
        for node_name, state_update in event.items():
                # Get the last message added by the node
                last_msg = state_update['messages'][-1]
                
                # Safely print the text
                if hasattr(last_msg, 'content'):
                    # Check if content is a list or string
                    content = last_msg.content
                    text = content[0]['text'] if isinstance(content, list) else content
                    print(f"[{node_name}]: {text}")