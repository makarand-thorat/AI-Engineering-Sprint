import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#EPISODIC STORAGE LOGIC

memory_file= "episodic_diary.json"

def commit_to_diary(event: str):
    diary= []
    if os.path.exists(memory_file):
        with open(memory_file,"r")as f:
            diary = json.load(f)
    
    diary.append(event)
    with open(memory_file,"w") as f:
        json.dump(diary,f,indent=4)

    print(f" EVENT logged:{event}")
    return "Event successfully logged to memory."

def search_diary(query: str):
    
    if not os.path.exists(MEMORY_FILE):
        return "The diary is currently empty."
    
    with open(MEMORY_FILE, "r") as f:
        diary = json.load(f)
    
    # Simple keyword search 
    results = [entry for entry in diary if query.lower() in entry.lower()]
    
    if not results:
        return f"No entries found related to '{query}'."
    return "Found these relevant past events:\n" + "\n".join(results)

#Load Existing diary entriies to 'ground' the agent at startup
past_episodes=""
if os.path.exists(memory_file):
    with open(memory_file,"r") as f:
        entires=json.load(f)
        past_episodes="\n".join([f"-{e}" for e in entries])

#AGENT SETUP
SYSTEM_INSTRUCTION = """
You are a Memory-Managed Assistant. 
You don't remember everything instantly, but you have a DIARY you can search.

- If the user tells you something new and important, use 'commit_to_diary'.
- If the user asks about the past or you need context, use 'search_diary' first.
"""

chat=client.chats.create(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[commit_to_diary,search_diary],
        automatic_function_calling=types.AutomaticFunctionCallingConfig()
    )
)

print("EPISODIC AGENT IS LIVE. TELL ME SOMETHING I SHOULD REMEMBER!(Type 'exit' to stop)")

while True:
    user_input=input("\nYou: ")
    if user_input.lower()=="exit":break

    response=chat.send_message(user_inexitput)
    print(f"\nAgent: {response.text}")