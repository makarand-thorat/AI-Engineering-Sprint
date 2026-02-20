import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#Chat session manages "Short-Term" buffer automatically
chat=client.chats.create(model="gemini-3-flash-preview")
print("Short-term Memory Demo (Type 'exit' to stop)")

while True:
    user_input=input("You: ")
    if user_input.lower()=="exit": break

    response=chat.send_message(user_input)
    print(f"AI: {response.text}")

#Try telling the ai something and in the next prompt ask it what did you say before