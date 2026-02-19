import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Tool for the agent to use
def calculate_shipping(weight: float):
    """Calculates shipping cost based on weight in kg."""
    rate = 5.0
    return {"cost": weight * rate}

# The ReAct System Instruction
REACT_PROMPT = """
You are a ReAct Agent. For every request:
1. Thought: Reason about what you need to do.
2. Action: Call the appropriate tool.
3. Observation: Look at the result.
4. Final Answer: Provide the final response.
"""

chat = client.chats.create(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        system_instruction=REACT_PROMPT,
        tools=[calculate_shipping],
        automatic_function_calling=types.AutomaticFunctionCallingConfig()
    )
)

# Test the Reasoning Loop
print("ReAct Agent initialized.")
response = chat.send_message("I have a 10kg package. How much will shipping cost?")
print(f"Agent Reasoning & Result:\n{response.text}")