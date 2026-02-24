import os
import chromadb
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Use the database we built on Day 6
chroma_client = chromadb.PersistentClient(path="./research_db")
collection = chroma_client.get_or_create_collection(name="wiki_research")

def add_knowledge(url: str):
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

SYSTEM_PROMPT = """
YOU ARE A SELF-CORRECTING RESEARCH ANALYST.

WORKFLOW:
1. SEARCH: Always search your memory first using 'search_knowledge'.
2. EVALUATE: If the search results are missing the answer, tell the user you need more info and use 'add_knowledge' if they provide a URL.
3. DRAFT: Create a response based ONLY on the retrieved context.
4. REFLECT: Before finalizing, perform a 'Self-Critique' for hallucinations or missing details.
5. FINAL: Present the refined answer with citations (URLs).

CONSTRAINT: If you find conflicting info, highlight the contradiction. Do not make up facts.
"""

# --- CHAT SESSION ---

chat = client.chats.create(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[add_knowledge, search_knowledge],
        automatic_function_calling=types.AutomaticFunctionCallingConfig()
    )
)
# Test the loop
print(" Day 7: Master Reflexive Agent Online.")
while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]: break
    response = chat.send_message(user_input)
    print(f"\nAgent: {response.text}")