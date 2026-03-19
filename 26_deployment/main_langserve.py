from fastapi import FastAPI
from langserve import add_routes
from agent import graph  
import uvicorn

app = FastAPI(
    title="Day 26: LangServe Developer API",
    version="1.0",
    description="Developer-focused API with Streaming and Playground"
)
configurable_graph = graph.with_config(
    {"configurable": {"thread_id": "playground_user"}}
)

add_routes(
    app,
    configurable_graph,
    path="/agent",
    config_keys=["configurable"]
)

if __name__ == "__main__":
    
    print("🚀 LangServe Playground available at: http://localhost:8001/agent/playground/")
    uvicorn.run(app, host="0.0.0.0", port=8001)