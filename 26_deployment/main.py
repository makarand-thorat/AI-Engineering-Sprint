from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent import graph,clear_thread_memory
import uvicorn

app = FastAPI(title="Day 26 : Production Agent API")

class ChatInput(BaseModel):
    message: str
    thread_id: str = "default-session"

class ChatOutput(BaseModel):
    response: str
    thread_id: str

@app.get("/")
async def health_check():
    return {"status": "online", "agent": "ready"}

@app.post("/chat",response_model=ChatOutput)
async def chat_with_agent(input_data: ChatInput):
    try:
        config = {"configurable": {"thread_id": input_data.thread_id}}
        inputs = {"messages": [HumanMessage(content=input_data.message)]}
        result = graph.invoke(inputs, config=config)
        final_answer = result["messages"][-1].content[0].get("text","")

        return ChatOutput(
            response=final_answer,
            thread_id=input_data.thread_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Error: {str(e)}")

@app.delete("/chat/{thread_id}")
async def reset_chat(thread_id: str):
    try:
        clear_thread_memory(thread_id)
        check = graph.get_state({"configurable": {"thread_id": thread_id}})
        print(f"Memory Status: {len(check.values.get('messages', []))} messages remaining.")
        return {"status": "success", "message": f"Memory for {thread_id} has been cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",port=8000)
