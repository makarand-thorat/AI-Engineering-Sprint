import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langsmith import Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith.evaluation import evaluate

load_dotenv()
client = Client()


from app import app as agent_graph 

def run_agent(dataset_input: dict):

    user_query = dataset_input.get("input")
    if not user_query and "messages" in dataset_input:
        user_query = dataset_input["messages"][0]["content"]

    result = agent_graph.invoke({"messages": [HumanMessage(content=user_query)]})

    return {"output": result["messages"][-1].content}


judge_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"))

def relevance_evaluator(run, example):
    """
    The Judge logic. It compares the agent's output to the original input.
    """
    agent_output = run.outputs.get("output")
    reference_input = example.inputs.get("question")
    
    prompt = f"""
    SYSTEM: You are a professional AI Auditor.
    USER INPUT: {reference_input}
    AGENT RESPONSE: {agent_output}
    
    CRITERIA: Did the agent accurately answer the math query?
    SCORE: Return ONLY a score between 1 and 5 (5 is perfect).
    """
    
    response = judge_llm.invoke(prompt)
    try:
        score = int(response.content.strip())
    except:
        score = 0 
        
    return {"key": "relevance", "score": score / 5}


if __name__ == "__main__":
    
    dataset_name = "test" 
    
    print(f" Running Eval on Dataset: {dataset_name}...")
    
    experiment_results = evaluate(
        run_agent, 
        data=dataset_name, 
        evaluators=[relevance_evaluator], 
        experiment_prefix="Math-Test-Run"
    )
    
    print("\n✅ Evaluation Complete!")
    print(f"📊 View results here: {experiment_results.experiment_name}")