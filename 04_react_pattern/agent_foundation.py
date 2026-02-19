import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- PILLAR 1 & 2: THE TOOLS & STANDARDS (FUNCTION CALLING + MCP) ---
# We define our "Knowledge Server" with clear types and docstrings
def get_product_inventory(product_name: str):
    """
    Standardized tool to check warehouse stock levels.
    Acts as an MCP-compliant data resource.
    """
    inventory = {"laptop": 15, "monitor": 0, "keyboard": 50}
    count = inventory.get(product_name.lower(), 0)
    print(f"Checking DB for {product_name}: Found {count}")
    return {"item": product_name, "stock_count": count}

def calculate_shipping_time(city: str):
    """Returns estimated shipping days for a specific city."""
    print(f"Calculating logistics for {city}...")
    return {"city": city, "days": 3 if city.lower() == "dublin" else 5}

# --- PILLAR 3: THE REASONING (REACT PATTERN) ---
# This system instruction forces the AI to follow the Thought-Action-Observation loop
SYSTEM_INSTRUCTION = """
You are a Logistics Reasoning Agent. You MUST follow this pattern for every request:
1. THOUGHT: What is the user asking? What information is missing?
2. ACTION: Use a tool to gather data.
3. OBSERVATION: What did the tool return?
4. FINAL ANSWER: Provide a grounded response based ONLY on observations.

If an item is out of stock, suggest checking back later.
"""

chat = client.chats.create(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[get_product_inventory, calculate_shipping_time],
        automatic_function_calling=types.AutomaticFunctionCallingConfig()
    )
)

def run_agent():
    print("Day 4 Super-Agent Online.")
    # Complex query to trigger multi-step reasoning
    query = "Can I order 1 laptop and 1 monitor for delivery to Dublin?"
    
    response = chat.send_message(query)
    print("\n--- AGENT REASONING PROCESS ---")
    print(response.text)

if __name__ == "__main__":
    run_agent()