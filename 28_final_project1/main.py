import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent import app as agent_graph
import uvicorn

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    
    inputs = {"messages": [HumanMessage(content=request.message)]}
    
    async def event_generator():
       
        async for event in agent_graph.astream_events(inputs, version="v2"):
            kind = event["event"]

            
            if kind == "on_tool_start":
                yield f"data: {json.dumps({'text': '🔍 Searching DuckDuckGo for context...\n'})}\n\n"

           
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                
                
                if hasattr(chunk, "content") and isinstance(chunk.content, list):
                    content = chunk.content[0].get("text", "") if chunk.content else ""
                else:
                    content = getattr(chunk, "content", "")
                
                if content:
                    yield f"data: {json.dumps({'text': content})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)