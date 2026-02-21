import os
import chromadb
import trafilatura
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#1.KNOWLEDGE BASE (RAG)

chroma_client = chromadb.PersistentClient(path="./research_db")
collection = chroma_client.get_or_create_collection(name="research_vault")

def add_web_knowledge(url: str):
    print(f"Scraping: {url}")
    downloaded=trafilatura.fetch_url(url)
    content=trafilatura.extract(downloaded, include_comments=False)

    if not content:
        return f"Could not extract content from {url}"

    #Semantic Chunking: Split by double newline to keep paragraphs intact
    chunk=[c.strip() for c in content.split("\n\n") if len(c.strip())>100]

    for i,chunk in enumerate(chunks):
        #Generate high-dimensional vector using embedding model
        emb_res=client.models.embed_content(
            model="text-embedding-004",
            contents=chunk
        )

        collection.add(
            embeddings=[emb_res.embeddings[0].values],
            documents=[chunk],
            metadatas=[{"source":url,"part":i}],
            ids=[f"{url}_{i}"]
        )
    return f"Success: Ingested {len(chunks)} semantic chunks from {url}."

def search_knowledge(query: str):
    #performs semantic search to find information regardless of exact keywords

    query_emb=client.models.embed_content(
        model="text-embedding-004",
        contents=query
    ).embeddings[0].values

    result=collection.query(query_emebeddings=[query_emb],n_results=3)
    return "\n---\n".join(results['documents'][0]) if results['documents'] else "No relevant info found."

    #2. Function Calling
def get_system_status():
    #Simulates a call to a live database or hardware sensor
    return{"status": "online", "load":"75%", "server":"DUblin-Primary-01"}

#3.THE AGENT

SYSTEM_PROMPT="""
    You are a Research & Operations Agent. 
1. Use 'add_web_knowledge' to learn about a topic from a URL.
2. Use 'search_knowledge' to retrieve info you've learned.
3. Use 'get_system_status' for real-time infrastructure data.

Analyze the relationship between research data and live system status to give deep insights.
    """

chat=client.chats.create(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
    system_instruction = SYSTEM_PROMPT,
    tools=[add_web_knowledge, search_knowledge, get_system_status],
    automatic_function_calling=types.AutomaticFunctionCallingConfig()
)
)

print("Day 6: Deep Researcher Ready.")
# Example workflow:
# 1. "Learn from https://en.wikipedia.org/wiki/Artificial_intelligence"
# 2. "Based on what you learned and our system status, is our server load normal for an AI hub?"

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]: break
    response = chat.send_message(user_input)
    print(f"\nAgent: {response.text}")