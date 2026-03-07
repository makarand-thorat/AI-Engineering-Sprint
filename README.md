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

## 📅 Day 9: Cycles & Conditionals — The ReAct Agent 🔄

**Goal:** Implement a self-correcting state machine that loops between reasoning and tool execution to satisfy complex, multi-step goals.

### 🏗️ System Architecture

This milestone implements the **ReAct (Reasoning + Acting)** pattern. By using LangGraph's cyclic capabilities, the agent can now perform internal loops to gather information or process data before ever returning a final result to the user.

### 1. The Reasoning Engine (Gemini 3 Flash)
- **Tool Binding:** Integrated Gemini 3.0 with a set of arithmetic tools. The model chooses tools based on the semantic intent of the user prompt.
- **System Instructions:** Injected a `SystemMessage` to maintain persona and reliability throughout the cycle.

### 2. The Logic Loop
- **Nodes:** - `our_agent`: The LLM reasoning node.
    - `tools`: A dedicated execution node for running Python functions.
- **Conditional Edges:** A `should_continue` router that inspects `tool_calls` to decide if the graph should cycle back to the agent or terminate.

### 3. State Management
- **`add_messages` Reducer:** Prevents message overwriting, allowing the agent to "remember" the results of tool executions from previous cycles.
- **Sequence Tracking:** Maintained a clean flow of `HumanMessage` -> `AIMessage (Tool Call)` -> `ToolMessage (Result)` -> `AIMessage (Final Answer)`.

### 🚀 Key Achievements
- **Cyclic Autonomy:** Built an agent capable of looping as many times as necessary to solve a problem (e.g., chained math operations).
- **Non-Linear Execution:** Moved away from "Step A to Step B" and into a true state-machine that routes data based on the AI's internal logic.
- **Stream Visualization:** Implemented state streaming to observe the AI's "thought process" and tool usage in real-time.

## 📅 Day 10: Tool Node Mastery & Automated Workflows 🛠️

**Goal:** Standardize agent actions by integrating LangGraph's pre-built `ToolNode` and implementing robust exit conditions for autonomous document management.

### 🏗️ System Architecture

I evolved the **Drafter** agent to delegate execution to a specialized `ToolNode`. This ensures the agent follows a strict **ReAct (Reasoning and Acting)** pattern:

1.  **Reasoning:** The agent (Gemini 3.0) determines if it needs to update or save a file.
2.  **Acting:** The `ToolNode` executes the Python functions (`update` or `save`).
3.  **Observation:** The graph cycles back to the agent or terminates based on the tool's success metadata.



### 1. The Reasoning Engine (Gemini 3 Flash)
- **Structured Tool Calling:** Integrated Gemini 3.0 with `update` and `save` tools. The model autonomously decides which tool to use based on the semantic intent of the user prompt.
- **Contextual Awareness:** Injected a `SystemMessage` that provides the current document state, allowing the AI to understand the context of modifications.

### 2. The Logic Loop
- **Nodes:** - `agent`: The LLM reasoning node.
    - `tools`: A dedicated execution node (`ToolNode`) for running Python functions.
- **Conditional Edges:** A `should_continue` router that inspects `ToolMessage` contents to decide if the graph should cycle back to the agent or terminate.



### 3. State Management
- **`add_messages` Reducer:** Prevents message overwriting, allowing the agent to "remember" the results of tool executions from previous cycles.
- **Workflow State:** Maintains a clean flow of interaction: Human Input -> Reasoning -> Tool Execution -> Verification.

### 🚀 Key Achievements
- **ToolNode Integration:** Replaced manual `if/else` tool routing with `langgraph.prebuilt.ToolNode`, significantly reducing code complexity.
- **Robust Exit Conditions:** Implemented a `should_continue` function to parse tool outputs and reliably break the autonomous loop upon successful file saving.
- **Context Retention:** Successfully maintained state across multiple reasoning cycles, enabling iterative document updates.

## 📅 Day 11: Agentic RAG — Knowledge-Augmented Intelligence 📚

**Goal:** Build a Retrieval-Augmented Generation (RAG) agent that autonomously decides when to consult external PDF documents to answer complex queries.

### 🏗️ System Architecture

This milestone moves beyond the agent's internal training data. By integrating a **Vector Database**, the agent can now perform "Open-Book" exams on specific datasets (Stock Market Performance 2024).

1.  **Ingestion:** PDFs are loaded via `PyPDFLoader`, split into semantic chunks, and embedded using `gemini-embedding-001`.
2.  **Storage:** Vectors are persisted locally in **ChromaDB**, allowing for lightning-fast semantic retrieval.
3.  **Agentic Retrieval:** The LLM doesn't just "get context." It **chooses** to use the `retriever_tool` only when the user's query requires specific data from the document.

### 🚀 Key Achievements

- **Persistent Vector Store:** Implemented disk-based storage for embeddings, ensuring the knowledge base doesn't vanish between sessions.
- **Dynamic Tool Usage:** The agent can call the retriever multiple times with different search queries to "triangulate" the best answer.
- **Source Attribution:** Configured system prompts to ensure the agent cites specific document sections, increasing factual reliability and reducing hallucinations.

## 📅 Day 12: Self-Correcting Coding Agent — The Debugging Loop 🛠️

**Goal:** Build an autonomous agent capable of writing Python code, executing it in a real environment, and using real-time error feedback to self-correct until a valid solution is reached.

### 🏗️ System Architecture

Today’s milestone introduces the **Cyclic Reasoning Pattern**. Unlike traditional linear pipelines, this agent operates within a "Loop of Truth"—it cannot provide a final answer until its generated code executes successfully.


1.  **Generation Node (`call_model`):** The LLM acts as a Senior Developer, interpreting the user's prompt to architect a Python solution.
2.  **Execution Node (`python_executor`):** A custom environment that runs the code and captures the output or the exact Stack Trace if it fails.
3.  **Self-Correction Loop:** If a failure is detected, the full history—including the faulty code and the specific error message—is sent back to the LLM for analysis.
4.  **State Management:** The system tracks "Execution Iterations" to ensure the agent has a set budget (e.g., 5 attempts) to fix the bug, preventing infinite loops and managing API costs.

### 🚀 Key Achievements

* **Operational Feedback Loops:** Moved beyond static prompting. The agent now uses external "ground truth" (terminal output) to validate its own reasoning.
* **Recursive Debugging:** Developed the logic for the agent to analyze tracebacks, identify syntax or logical errors, and provide iterative fixes autonomously.
* **Stateful Iteration Tracking:** Implemented an "Agentic Kill-Switch" within the StateGraph to manage computational resources and ensure system stability.
* **Dynamic Tool Calling:** Orchestrated a seamless transition between the "Thinker" (LLM) and the "Doer" (REPL Tool).


## 📅 Day 13: Persistent AI Agents — The MySQL Memory Layer 🧠💾
**Goal**: Transform the self-correcting agent into a production-ready system by migrating from volatile RAM-based memory to a persistent MySQL database backend.

### 🏗️ System Architecture
Today’s milestone introduces Durable State Management. By integrating a relational database, the agent's conversation history and internal reasoning (checkpoints) are preserved even if the script crashes or the server restarts.

1.  **Persistence Layer (PyMySQLSaver):** Replaces the temporary MemorySaver. This layer connects the LangGraph workflow to a dedicated MySQL schema (langgraph_db).

2.  **Checkpointing Engine:** After every node execution (e.g., call_model or tools), a binary "snapshot" of the entire AgentState is serialized and saved to SQL tables.

3.  **Thread-Based Retrieval:** Uses a unique thread_id to act as a lookup key. This allows the agent to distinguish between different users and resume specific conversations instantly.

4.  **Schema Automation:** Implemented checkpointer.setup(), which automatically architects the required relational tables (checkpoints, checkpoint_blobs, checkpoint_writes) within the database.

### 🚀 Key Achievements
*  **Long-Term Memory:** Successfully moved the agent's "brain" from temporary memory to a permanent disk-based storage system.

*  **Session Resumption:** Enabled the ability to stop the Python process and resume a complex debugging task hours later without losing progress.

*  **Environment-Driven Security:** Decoupled sensitive database credentials from the logic layer by implementing a secure .env configuration.

*  **Multi-User Scalability:** Established a foundation where unique thread_id values allow one agent instance to manage hundreds of independent, persistent conversations.

## 📅 Day 14: Project 1 — Autonomous Research Assistant 🕵️‍♂️📑

**Goal:** Build a production-ready autonomous research agent that leverages real-time web browsing and automated file persistence to synthesize complex topics into structured notes.

### 🏗️ System Architecture

Today’s milestone marks the transition from simple chat loops to a **Multi-Tool Orchestration** system. The agent acts as a controller, deciding which tools to call and when the research objective has been met.

1. **Search Node (`duckduckgo_search`):** Provides the agent with live access to the internet, bypassing the LLM's static knowledge cutoff.
2. **Logic Engine (Gemini 1.5 Flash):** Acts as the "Reasoning Layer." It evaluates search results to determine if the user's query is fully answered or if further searching is required.
3. **Persistence Node (`save_research_note`):** A custom tool decorated with `@tool` that allows the agent to interact with the local file system to save markdown notes.
4. **Custom Router:** A manual routing node that inspects the state for `tool_calls`. This determines the flow: **Agent ➔ Router ➔ Action (Tools) ➔ Agent.**

### 🚀 Key Achievements

* **Autonomous Tool Use:** Successfully implemented the **ReAct (Reasoning and Acting)** pattern where the LLM independently decides to use search or save tools.
* **Dynamic File Management:** The agent demonstrated "Creative Agency" by intelligently renaming files (e.g., `ai_trends.md`) based on research context rather than just using generic defaults.
* **Manual Routing Logic:** Built a custom router function to manage the graph flow, providing more transparency and control than prebuilt conditions.
* **Persistent Research:** Continued using the **MySQL Checkpointer** from Day 13, ensuring that even complex, multi-step research sessions are durable and resumable.


## 📅 Day 15: Multi-Agent Orchestration (The Supervisor Pattern)


**Goal:** Transition from a "Swiss Army Knife" single agent to a professional "Kitchen Staff" architecture. Today's goal was to build a system where a central **Supervisor** coordinates specialized **Researcher** and **Writer** agents to produce a technical report.

### 🏗️ Architecture: The Orchestrator Pattern
In this design, agents don't talk to each other directly (Choreography); instead, they report back to a central "Brain" (Orchestration).

### The Workflow:
1.  **User Input:** "Research 2026 tech trends and save to report.md."
2.  **Supervisor:** Analyzes the state and delegates the task to the **Researcher**.
3.  **Researcher:** Executes parallel web searches and returns the data.
4.  **Supervisor:** Sees the data is ready and delegates the task to the **Writer**.
5.  **Writer:** Formats the findings and uses the `write_file` tool.
6.  **Supervisor:** Detects completion and signals the end of the process.

### 🛠️ Technical Challenges & Fixes

### 1. The "Turn-Order" Constraint (Gemini Specific)
**Problem:** Gemini's API enforces a strict "User-Assistant-Tool" sequence. In multi-agent loops, the history often results in multiple "Assistant" turns in a row, causing a `400 INVALID_ARGUMENT` error.
**Fix:** Implemented a **Context Reset**. Before invoking a worker, we wrap the relevant history into a fresh `HumanMessage`. This "tricks" the model into seeing a new user turn, ensuring API compliance.

### 2. Parallel Tool Handling
**Problem:** The Researcher often calls multiple tools simultaneously. LangGraph stores these as a `list` of messages, which caused an `AttributeError` when trying to access `.content` directly.
**Fix:** Added a robust check in the Supervisor to detect `list` objects and join the contents into a single string for analysis.


### 🚀 Key Features
- **Iteration Control:** Added a safety counter to prevent infinite loops (set to 1 full cycle).
- **Specialized Prompting:** Each worker has a narrow scope, increasing accuracy and reducing "context dilution."
- **State Management:** Uses a shared `TypedDict` state to pass the "baton" between agents.

## 📅 Day 16: CrewAI Fundamentals — Building a Research Team


**Goal:** Transition from manual graph-based agents to a high-level **Agentic Framework**. Today, I built a two-agent "Crew" consisting of a **Senior Research Analyst** and a **Tech Content Strategist** to automate the end-to-end process of researching and reporting on emerging tech trends.

### 🏗️ Architecture: Sequential Multi-Agent Crew
Unlike simple chains, CrewAI uses a "Role-Playing" architecture where agents are defined by their **Role**, **Goal**, and **Backstory**. This provides a much deeper cognitive context for the LLM.

#### The Team:
1.  **Senior Research Analyst:** - **Goal:** Uncover cutting-edge developments in a specific topic.
    - **Tools:** Powered by `SerperDevTool` for real-time Google Search access.
2.  **Tech Content Strategist:** - **Goal:** Translate complex research into an engaging, 3-point blog post.
    - **Handoff:** Automatically receives the Researcher's output as its input.

### 🛠️ Key Technical Features

#### 1. Sequential Process Management
I implemented a `Process.sequential` workflow. This ensures a strict linear progression:
- **Task 1 (Research):** Analyzes 2026 breakthroughs and outputs 3 key findings.
- **Task 2 (Writing):** Takes those specific findings and formats them into a professional markdown report.

#### 2. Native Gemini Integration
By using the `langchain_google_genai` provider, I integrated **Gemini 1.5 Flash** as the brain for both agents. This allows for high-speed reasoning while maintaining low token costs.

#### 3. Automated File Delivery
Instead of just printing to the console, I configured the final task with the `output_file="crew_report.md"` parameter. This ensures the agentic workflow results in a tangible asset saved directly to the local workspace.

### 📝 Lessons Learned
- **Framework over Logic:** CrewAI abstracts away the "state management" and "router" logic needed in LangGraph, allowing the developer to focus on **Agent Personas**.
- **Expected Output:** Defining the `expected_output` for each task is the most critical step to prevent agent "hallucination" or scope creep.
- **Tooling:** Adding the `SerperDevTool` effectively gave the agents "eyes" on the current internet, bridging the gap between training data and real-time facts.

## 📅 Day 17: LangGraph — Smart Routing & Command Handoffs

**Goal:** Implement a "Concierge Pattern" using LangGraph. Today, I built a system that uses an LLM-based **Router** to dynamically triage user requests to specialized expert nodes (Math vs. Creative) using the modern `Command` pattern.


### 🏗️ Architecture: The Concierge Pattern
Unlike basic linear chains, this graph uses a "Zero-Edge" approach for internal routing.

1.  **Router (Concierge):** Uses Gemini 3 Flash to analyze intent. Instead of hard-coded keywords, it intelligently understands whether a query requires logic/math or creative writing.
2.  **Specialists:** Two distinct nodes (`math_expert` and `creative_expert`) that only execute when called by the Router.
3.  **Command Pattern:** Utilized the `langgraph.types.Command` object to handle both the state update and the navigation (`goto`) in a single return statement.


### 🛠️ Key Technical Wins

1. **LLM-Based Triage**
Moved away from fragile `if "math" in query` checks. By using a small "Router Prompt," the system can now handle complex natural language (e.g., "What is 15% of 450?") and route it correctly.

2. **Handling Multimodal Content Blocks**
Navigated the Gemini 3 Flash output structure. Since the model returns a `list[dict]` for content (to support text + image blocks), I implemented direct indexing to extract the `decision_text` cleanly.

3. **State Management**
Used the built-in `MessagesState` to maintain a clean chat history while allowing the specialists to access the original human query through simple list indexing (`state["messages"][0]`).
---

Developed by **Makarand Thorat**
