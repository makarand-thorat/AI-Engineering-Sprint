import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# MCP Concept: Decouple the tool from the code logic
# We define tools as an "Infrastructure Layer"
class WarehouseServer:
    @staticmethod
    def list_inventory():
        """Returns the list of current stock items."""
        return ["Laptop", "Monitor", "Keyboard"]

# Registering the tool using the standardized list
mcp_tools = [WarehouseServer.list_inventory]

chat = client.chats.create(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(tools=mcp_tools)
)

print("MCP Standardized Tool Connected.")
response = chat.send_message("What do we have in stock?")
print(f"Gemini: {response.text}")