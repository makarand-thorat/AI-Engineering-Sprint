import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#Step 1: Define a tool
def get_order_status(order_id: str):
    #Retrieve shipping status of customer's order

    database={"101": "Shipped", "102":"Processing", "103":"Delivered"}
    status= database.get(order_id,"Order ID not found")
    print(f"System checked databse for ID:{order_id}")
    return{"order_id": order_id, "status":status}

#Step 2: Register tool and chat
chat=client.chats.create(
            model="gemini-3-flash-preview",
            config={"tools": [get_order_status]}
        )

#Step 3: Test

response=chat.send_message("where is my order #101?")
print(f"Gemini:{response.text}")