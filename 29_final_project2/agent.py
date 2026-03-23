import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Annotated, TypedDict
from langchain_core.messages import AIMessage, ToolMessage,SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState

load_dotenv()
search_tool = DuckDuckGoSearchRun()

tools = [search_tool]
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key= os.getenv("GEMINI_API_KEY")
    ).bind_tools(tools)


def evaluate_output(email_content: str):
    print("\n--- 🔍 DEBUG: STARTING EVALUATION ---")
    
    try:
        evaluator_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.1)
        
        prompt = f"""
        Grade this email draft for a VP-level partnership:
        "{email_content}"

        CRITICAL: Your entire response must be a single JSON object. 
        Do not use markdown backticks.
        Format: {{"score": 8, "reasoning": "your text here"}}
        """
        
        response = evaluator_llm.invoke(prompt)
        raw_text = response.content.strip()

        start_index = raw_text.find("{")
        end_index = raw_text.rfind("}")
        
        if start_index == -1 or end_index == -1:
            print("❌ Error: No JSON brackets found in response.")
            return {"score": 0, "reasoning": "LLM failed to provide JSON format."}


        json_string = raw_text[start_index : end_index + 1]

        parsed_data = json.loads(json_string)
        
        print(f"✅ Successfully Parsed! Score: {parsed_data.get('score')}")
        return parsed_data

    except Exception as e:
        print(f"❌ EVALUATION ERROR: {e}")
        return {"score": 0, "reasoning": f"System error: {str(e)}"}


def call_model(state):
    system_instruction = SystemMessage(content=(
        "You are a 'Company Researcher & Email Drafter'. "
        "Your workflow is: "
        "1. Search for the company's mission and recent news using DuckDuckGo. "
        "2. Analyze the findings. "
        "3. Draft a high-conversion, personalized partnership email. "
        "Always provide the research summary before the email draft."
    ))

    #GUARDRAIL
    last_message = state["messages"][-1].content.lower()
    prohibited_keywords = ["crypto scam", "hack", "bypass"]
    if any(word in last_message for word in prohibited_keywords):
        return {"messages": [AIMessage(content="I'm sorry, I can only assist with corporate research and professional email drafting.")]}

    messages = [system_instruction] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def call_tool(state):
    last_message = state["messages"][-1]
    results = []

    for tool_call in last_message.tool_calls:
        print(f"🤖 LLM requested search: {tool_call['args']}")
        observation = search_tool.invoke(tool_call["args"])
        results.append(ToolMessage(
            tool_call_id=tool_call["id"],
            content=str(observation)
        ))

    return {"messages": results}

def should_continue(state):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "end"

workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tool)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools", 
        "end": END        
    }
)
workflow.add_edge("tools", "agent")
app = workflow.compile()