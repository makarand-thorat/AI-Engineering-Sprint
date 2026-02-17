Set-Content -Path "README.md" -Value @"
# 🤖 AI Meeting Minutes Extractor

Part of the **AI Engineering Sprint 2026**. This tool leverages the **Gemini 3 Flash** model to transform raw, unstructured meeting transcripts into high-quality, structured JSON data.

## 🌟 Key Features
- **Structured Extraction:** Uses Instructor and Pydantic to force LLM output into a strict, predictable JSON schema.
- **Action Item Tracking:** Automatically identifies tasks, assigns owners, and categorizes priority levels.
- **Sentiment Analysis:** Detects the meeting's emotional tone and overall mood.
- **Secure by Design:** Implements industry-standard .env environment variables.

## 🛠 Tech Stack
- **Language:** Python 3.9+
- **LLM API:** Google Gemini 3 Flash
- **AI Orchestration:** Instructor

## 🚀 Getting Started

### 1. Installation
\`\`\`powershell
pip install instructor pydantic google-genai python-dotenv
\`\`\`

### 2. Configuration
Create a \`.env\` file and add:
\`\`\`text
GEMINI_API_KEY=your_key_here
\`\`\`

---
Developed by **Makarand Thorat**
