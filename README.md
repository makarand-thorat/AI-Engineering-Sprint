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
---

Developed by **Makarand Thorat**
