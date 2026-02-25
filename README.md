# 🚀 30-Day AI Engineering Sprint

This repository documents my journey through the **AI Engineering Sprint 2026**, moving from basic LLM calls to complex, production-ready AI agents.

---

## 🛠 Global Tech Stack
- **Language:** Python 3.13
- **Model:** Google Gemini 3.0 Flash (via `google-genai`)
- **Environment Management:** Virtual Environments (`venv`) & `python-dotenv`

---

## 📅 Day 1: Structured Meeting Extraction
**Goal:** Transform messy transcripts into machine-readable data.

- **Folder:** `/01_meeting_extractor`
- **Core Concept:** Using **Pydantic** and **Instructor** to enforce a schema on LLM outputs.
- **Outcome:** Extracts tasks, owners, priorities, and meeting sentiment into a structured JSON format.

## 📅 Day 2: RAG-Based Transcript Chatbot
**Goal:** Chat with long documents without hitting context limits.

- **Folder:** `/02_chat_with_transcript`
- **Core Concept:** **Retrieval-Augmented Generation (RAG)**.
- **Key Features:**
  - **Recursive Chunking:** Splitting text into overlapping segments using `langchain-text-splitters`.
  - **Contextual Retrieval:** A keyword-based search engine to find the most relevant transcript part for a user's question.
  - **Grounded Responses:** The AI is instructed to answer *only* based on the provided transcript chunks, reducing hallucinations.

## 📅 Day 3: Multimodal Audio Intelligence
**Goal:** Transition from text-based processing to native audio "listening" and analysis.

- **Folder:** `/03_audio_processor`
- **Core Concept:** **Native Multimodality**. Instead of using a separate Speech-to-Text (STT) model, we leverage Gemini’s ability to process raw audio waves directly for better context and tone detection.
- **Key Features:**
  - **Asynchronous File Handling:** Implementing a state-check loop to manage the `PROCESSING` status of large media files in the Google File API.
  - **Automated Speaker Diarization:** Identifying and labeling different speakers (Speaker 1, Speaker 2) based on vocal characteristics.
  - **Temporal Logic:** Generating precise `[MM:SS]` timestamps linked to specific transcript segments.
  
## 📅 Day 4: Agentic Foundations (Combined Milestone)
**Goal:** Merge Function Calling, MCP Standards, and ReAct Reasoning into a single autonomous agent.

- **Folder:** `/04_agentic_foundations`
- **Core Concepts:**
  - **Function Calling:** Defined local Python tools that the model can trigger to interact with the real world.
  - **MCP (Model Context Protocol):** Designed standardized tool interfaces to allow for clean, interoperable data exchange between the AI and backend.
  - **ReAct Pattern:** Implemented the `Thought -> Action -> Observation` loop, ensuring the model reasons through complex, multi-step tasks before answering.

### 🧠 Logic Flow:
1. **Thought:** AI identifies that it needs stock data and shipping times.
2. **Action:** AI triggers `get_product_inventory` and `calculate_shipping_time`.
3. **Observation:** AI sees that Monitors are out of stock (0) and shipping to Dublin takes 3 days.
4. **Final Answer:** AI informs the user about the laptop and the monitor shortage specifically.

## 📅 Day 5: Multi-Tiered Agent Memory 🧠

**Goal:** Bridge the gap between temporary chat context and permanent episodic recall by implementing a tiered memory architecture.


### 🛠️ Technical Implementation

This milestone demonstrates two distinct "temporal" layers of an AI brain:

### 1. Short-Term Memory (`05_short_term_memory.py`)
* **Mechanism:** Utilizes the Gemini `ChatSession` to manage the immediate context window.
* **Function:** Maintains the "thread" of a conversation, allowing the model to resolve pronouns (e.g., "it", "that") and follow-up on previous sentences.
* **Technical Note:** In the 2026 `google-genai` SDK, the session history is managed via an internal `_history` state that grows by 2 entries (User + Model) for every interaction.

### 2. Episodic Memory & Selective Recall (`05_episodic_recall.py`)
* **Mechanism:** A persistent JSON-based "Diary" combined with autonomous tool-calling.
* **Dual-Tooling:**
    * `commit_to_diary`: Triggered when the AI identifies significant facts or preferences to save them to `episodic_diary.json`.
    * `search_diary`: Enables the agent to perform targeted keyword searches over past interactions.
* **Advantage:** By using **Selective Recall**, we avoid "context stuffing." The agent only retrieves relevant memories, saving tokens and maintaining high reasoning quality.

### 🚀 Key Achievements
- **Persistence:** The agent now remembers user preferences (like names, project goals, or travel plans) even after the script is restarted.
- **Autonomous Decision Making:** The agent decides *what* is worth remembering and *when* it needs to search its past.
- **Scalable Architecture:** Laid the foundation for Semantic Search (Day 6) by separating storage from retrieval logic.

## 📅 Day 6: The Deep Researcher Agent 🕵️‍♂️

**Goal:** Build a production-grade RAG (Retrieval-Augmented Generation) system that autonomously ingests web data, stores it in a vector database, and synthesizes it with live system status.

---

### 🏗️ System Architecture

This project implements a "Full-Stack" Agentic workflow involving three core layers:

### 1. The Ingestion Layer (`trafilatura`)
- **Main Content Extraction:** Uses `trafilatura` to strip away "web noise" (HTML boilerplate, ads, navbars) to ensure only high-signal text is fed to the model.
- **Semantic Chunking:** Documents are split by paragraph boundaries (`\n\n`) to preserve the semantic integrity of the information.

### 2. The Semantic Memory (`ChromaDB` + `text-embedding-004`)
- **Vector Embeddings:** Text chunks are converted into 768-dimensional vectors using Google's `text-embedding-004`.
- **Persistent Storage:** Utilizes a local `chromadb` instance, allowing the agent to retain "learned" knowledge indefinitely across script restarts.
- **Vector Search:** Enables the agent to find information based on **conceptual meaning** rather than literal keyword matches.

### 3. The Reasoning Engine (Gemini 3.0 Flash)
- **Multi-Tool Synthesis:** The agent can autonomously decide to:
    1. Scrape a new URL to update its knowledge.
    2. Search the existing vector database for historical context.
    3. Query a live "System Status" function to compare research with real-time reality.

## 📅 Day 7: Reflexive Knowledge Loops & Self-Correction 

**Goal:** Advance from "Simple RAG" to "Agentic RAG" by implementing a self-critique loop that identifies information gaps and corrects hallucinations before responding.

---

### 🧠 The Concept: Reflection Pattern
In Day 6, the agent blindly trusted its first search result. In Day 7, we introduced **Cognitive Reflection**. The agent now follows an internal "Standard Operating Procedure" (SOP):
1. **Detect Gaps:** Evaluates if the current memory (Vector DB) is sufficient.
2. **Autonomous Research:** Triggers the scraper if more data is required.
3. **Draft & Critique:** Writes a response, then "proofreads" it against the source text to catch errors (like temporal contradictions).


### 🚀 Key Implementation: The Master System Prompt
The core of Day 7 is moving logic out of Python loops and into the **System Instruction**. This allows the model to manage its own tool-use and reflection phases natively.

```python
SYSTEM_PROMPT = """
YOU ARE A SELF-CORRECTING RESEARCH ANALYST.
WORKFLOW:
1. SEARCH: Always search memory first.
2. EVALUATE: If results are insufficient, use 'add_knowledge'.
3. REFLECT: Critique your draft for hallucinations or logic errors.
4. FINAL: Present the refined answer with citations.
"""
```
## 📅 Day 8: Orchestration & State Machines with LangGraph 🔄

**Goal:** Transition from manual Python loops to a professional orchestration framework by mastering the 5 core graph patterns in LangGraph.


### 🏗️ System Architecture

This milestone marks the shift from "scripting" to **System Architecture**. By decoupling the workflow logic (the "Conveyor Belt") from the model's intelligence (the "Worker"), I’ve built a robust skeleton for deterministic state management.

### 1. The State Engine (`TypedDict`)
- **Centralized Schema:** Defined a structured `State` dictionary that serves as the "single source of truth" passed between nodes.
- **Context Preservation:** Ensures every step of the process has access to updated variables and history without manual hand-offs.

### 2. The Five Pillars of Logic
I implemented five foundational patterns using pure Python logic to verify the infrastructure:
- **Single & Multi-Input:** Mastering state initialization and complex data schemas.
- **Sequential:** Orchestrating deterministic "Assembly Line" pipelines.
- **Conditional (Routing):** Implementing logic-based decision paths to navigate the graph.
- **Looping (Cyclic):** Creating the "Agentic" engine that allows for retries, refinement, and self-correction.

### 3. Separation of Concerns
- **Nodes as Workers:** Each node is a discrete function responsible for one specific state transformation.
- **Edges as Orchestrators:** Defines the "road map," controlling the exact flow of execution based on specific conditions.

### 🚀 Key Achievements
- **Deterministic Reliability:** Verified that complex branching and looping logic works with 100% predictability before adding LLM uncertainty.
- **Modular Design:** Moved away from monolithic scripts to a modular graph that can scale with new tools and personas.
- **Architectural Readiness:** Prepared the system to host any LLM (Gemini, Claude, or local) as a "plug-and-play" component within the graph.

---

Developed by **Makarand Thorat**
