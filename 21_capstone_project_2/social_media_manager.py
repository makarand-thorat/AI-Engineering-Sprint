import os
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph.message import add_messages
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage

load_dotenv()

search_tool = DuckDuckGoSearchRun()
tools = [search_tool]
tool_node = ToolNode(tools)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    api_key=os.getenv("GEMINI_API_KEY")
    )
llm_with_tools = llm.bind_tools(tools)


class SocialManagerState(TypedDict):
    topic: str
    messages: Annotated[Sequence[BaseMessage], add_messages]
    post_draft: str
    critique: str
    is_ready: bool



def researcher_node(state: SocialManagerState):
    search_count = sum(1 for m in state["messages"] if hasattr(m, 'tool_calls'))
    
    print(f"🔍 Researcher: Step {search_count + 1}...")

    if search_count >= 2:
        print("⚠️ Max searches reached. Forcing transition to Creator.")
        return {"messages": [HumanMessage(content="Search limit reached. Use the data collected so far.")]}

    prompt = [
        SystemMessage(content="You are a trend researcher. Use the search tool once to find news. If you already see search results in the history, summarize them and do NOT search again."),
        HumanMessage(content=f"Find the latest trends for {state['topic']}.")
    ]

    response = llm_with_tools.invoke(prompt + list(state["messages"]))
    return {"messages": [response]}

def creator_node(state: SocialManagerState):
    print("✍️ Creator: Drafting the post...")
    research_data = state["messages"][-1].content
    prompt = f"Using this research: {research_data}, write a viral LinkedIn post about {state['topic']}. Focus on a strong hook and short post of 50 words"
    response = llm.invoke(prompt)
    return {"post_draft": response.content}

def critic_node(state: SocialManagerState):
    print("🧐 Critic: Reviewing content...")
    prompt = f"Critique this post: {state['post_draft']}. Does it sound like an AI wrote it? Is the hook strong and is it less than 50 words? Respond with 'READY' if it's perfect, otherwise provide short feedback."
    response = llm.invoke(prompt)
    is_ready = "READY" in response.content.upper()
    return {"critique": response.content, "is_ready": is_ready}


workflow = StateGraph(SocialManagerState)

workflow.add_node("researcher", researcher_node)
workflow.add_node("tools", tool_node)
workflow.add_node("creator", creator_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("researcher")


workflow.add_conditional_edges(
    "researcher", 
    tools_condition, 
    {"tools": "tools", "__end__": "creator"}
)
workflow.add_edge("tools", "researcher")

workflow.add_edge("creator", "critic")

workflow.add_conditional_edges(
    "critic",
    lambda state: "approve" if state["is_ready"] else "rewrite",
    {"approve": END, "rewrite": "creator"}
)


memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "ddg_session_1"}}
initial_input = {"topic": "Autonomous AI Agents in 2026", "messages": []}



print("\n--- Starting Social Media Manager (Powered by DuckDuckGo) ---")
for event in app.stream(initial_input, config):
    for node, values in event.items():
        if node == "creator":
            print(f"\n📝 DRAFT:\n{values['post_draft']}\n")
        elif node == "critic":
            print(f"💬 CRITIC FEEDBACK: {values['critique']}")

print("\n✨ FINAL APPROVED POST ✨")
print(app.get_state(config).values["post_draft"])