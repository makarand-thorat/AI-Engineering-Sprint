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

## Day 5: Multi-Tiered Agent Memory 🧠

**Goal:** Bridge the gap between temporary chat context and permanent episodic recall by implementing a tiered memory architecture.

---

## 🛠️ Technical Implementation

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

---

## 🚀 Key Achievements
- **Persistence:** The agent now remembers user preferences (like names, project goals, or travel plans) even after the script is restarted.
- **Autonomous Decision Making:** The agent decides *what* is worth remembering and *when* it needs to search its past.
- **Scalable Architecture:** Laid the foundation for Semantic Search (Day 6) by separating storage from retrieval logic.
---

Developed by **Makarand Thorat**
