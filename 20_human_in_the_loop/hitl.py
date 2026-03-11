import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

#Define Agent State
class AgentState(TypedDict):
    requirement: str
    code: str
    review : str
    approval: bool


#Define Nodes 

llm = ChatGoogleGenerativeAI(
    model = "gemini-3-flash-preview",
    api_key= os.getenv("GEMINI_API_KEY")
)


def coder_node(state : AgentState):
    print("Coder is writing code..")
    prompt = f"Write Python code for: {state['requirement']} Previous review: {state.get('review', 'None')}"
    response = llm.invoke(prompt)
    return {"code":response.content}

def reviewer_node(state : AgentState):
    print("Reviewer is checking code..")
    prompt = f"Review this code  {state['code']} and respond only in two words APPROVED OR REJECTED no summary needed just two words"
    response = llm.invoke(prompt)
    approval = "APPROVED" in response.content[0].get("text","").upper()
    return {"review": response.content, "approval" : approval}

def human_approval_node(state: AgentState):
    return state

workflow = StateGraph(AgentState)

workflow.add_node("coder",coder_node)
workflow.add_node("reviewer",reviewer_node)
workflow.add_node("human_approval", human_approval_node)

workflow.set_entry_point("coder")
workflow.add_edge("coder","reviewer")

#BREAKPOINT LOGIC

def router(state : AgentState):

    if state["approval"]:
        return "yes"
    else:
        return "no"

workflow.add_conditional_edges("reviewer",router,
{
    "yes" : "human_approval",
    "no": "coder"
})
workflow.add_edge("human_approval", END)

memory = MemorySaver()
app = workflow.compile(checkpointer = memory, interrupt_before=["human_approval"])

config = {"configurable": {"thread_id": "1"}}

print("----Statrting Workflow----")
for event in app.stream({"requirement": "Small code to reverse a string in python, only 2-3 lines"}, config):
    if "coder" in event:
        code_out = event["coder"]["code"][0].get("text","")
        print("\n[CODER OUTPUT]:")
        print(code_out)
        
    elif "reviewer" in event:
        review_out = event["reviewer"]["review"][0].get("text","")
        print("\n[REVIEWER OUTPUT]:")
        print(review_out)


print("\n PAUSED FOR HUMAN REVIEW")
current_state = app.get_state(config)
proposed_code = current_state.values.get("code")
print(f"--- PROPOSED CODE ---\n{proposed_code}\n---------------------")
user_input = input("The AI thinks it's done. Press Enter to 'deploy' or type feedback to send back: ")

if not user_input:
    print("Human approved. Resuming Completion..")
    for event in app.stream(None, config):
       print("---END---")
else:
    print("Sending human feedback to the coder..")
    app.update_state(config,{"review": user_input, "approval": False},as_node="reviewer")
    for event in app.stream(None,config):
       print(event)