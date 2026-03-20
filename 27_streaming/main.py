import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent import graph
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title = "Day 27: Streaming AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your HTML file to talk to the API
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    message: str
    thread_id: str = "stream_user_1"

@app.post("/chat/stream")
async def chat_streaming(input_data: ChatInput):
    config = {"configurable": {"thread_id": input_data.thread_id}}
    inputs = {"messages": [HumanMessage(content=input_data.message)]}

    async def event_generator():
        async for event in graph.astream_events(inputs,config,version="v2"):
            
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                content = ""
                if hasattr(chunk, "content") and isinstance(chunk.content, list):
                    if len(chunk.content) > 0 and "text" in chunk.content[0]:
                        content = chunk.content[0]["text"]
                elif hasattr(chunk, "content") and isinstance(chunk.content, str):
                    content = chunk.content
                if content:
                    yield f"data: {json.dumps({'text':content})}\n \n"
    
    return StreamingResponse(event_generator(),media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",port=8000)