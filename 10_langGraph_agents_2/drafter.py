from langchain_core.messages.base import BaseMessage
from typing import Annotated, Sequence, TypedDict
import os
from dotenv import load_dotenv  
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()
document_content = ""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage],add_messages]

@tool
def update(content: str)-> str:
    """updates document with provided content"""
    global document_content
    document_content = content
    return f"Document has been updated the current content is:\n {document_content}"

@tool
def save(filename: str)->str:
    """Saves the current document to a text file and finish the process.  
    Args:
    filename: Name for the text file.
    """
    global document_content

    if not filename.endswith('.txt'):
        filename=f"{filename}.txt"

    try:
        with open(filename,'w') as file:
            file.write(document_content)
        print(f"\n Document has been saved to : {filename}")
        return f"Doucment has been saved successfully to '{filename}'."
    except Exception as e:
        return f"Error saving document: {str(e)}"


tools=[update,save]
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key=os.getenv("GEMINI_API_KEY"),
    ).bind_tools(tools)


def model_call(state:AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are Drafter, a helpful writing assistant. You are going to help the user update and modify documents.
    
    - If the user wants to update or modify content, use the 'update' tool with the complete updated content.
    - If the user wants to save and finish, you need to use the 'save' tool.
    - Make sure to always show the current document state after modifications.
    
    The current document content is:{document_content}
    """)

    if not state["messages"]:
       user_input = "I'm ready to helo you update a document. what would you like to create?"
       user_message = HumanMessage(content=user_input)
    else:
        user_input = input("\nWhat would you like to do with the document? ")
        print(f"\n USER: {user_input}")
        user_message = HumanMessage(content=user_input)
    all_messages = [system_prompt] + list(state["messages"]) + [user_message]
    response = llm.invoke(all_messages)
    print(f"\n AI: {response.text}")

    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f" USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": [user_message, response]}

def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end the conversation."""

    messages = state["messages"]
    
    if not messages:
        return "continue"
    
    # This looks for the most recent tool message....
    print(f"DEBUG: Last message type: {type(messages[-1])}")
    print(f"DEBUG: Last message content: {messages[-1].content}")
    for message in reversed (messages):
        # ... and checks if this is a ToolMessage resulting from save
        
        if (isinstance(message, ToolMessage) and 
            "saved" in message.content.lower() 
            ):
            return "end" # goes to the end edge which leads to the endpoint
    print("Entered in continue blocks")  
    return "continue"

def print_messages(messages):
    """Function I made to print the messages in a more readable format"""
    if not messages:
        return
    
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"\n🛠️ TOOL RESULT: {message.content}")

graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("our_agent")
graph.add_edge("our_agent", "tools")
graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "our_agent",
        "end": END,
    },
)

app = graph.compile()

def run_document_agent():
    print("\n ===== DRAFTER =====")
    
    state = {"messages": []}
    
    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    
    print("\n ===== DRAFTER FINISHED =====")

if __name__ == "__main__":
    run_document_agent()