import os
from dotenv import load_dotenv
import instructor
from google import genai
from schema import MeetingSummary


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
instr_client = instructor.from_genai(client)

# 3. Load your transcript
with open("transcript.txt", "r") as f:
    transcript_text = f.read()


try:
    response = client.chat.completions.create(
        model="gemini-3-flash-preview", 
        config={"tools": []}, 
        messages=[{"role": "user", "content": transcript_text}],
        response_model=MeetingSummary,
    )

    print(f"\n✅ SUCCESS! PROJECT: {response.title}")
    print(f"Sentiment: {response.sentiment}")
    print("-" * 30)
    for item in response.action_items:
        print(f"Owner: {item.owner} | Task: {item.task} ({item.priority})")

except Exception as e:
    print(f" Error: {e}")