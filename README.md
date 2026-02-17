# 🤖 AI Meeting Minutes Extractor

Part of the **AI Engineering Sprint 2026**. This tool leverages the **Gemini 3 Flash** model to transform raw, unstructured meeting transcripts into high-quality, structured JSON data.

## 🌟 Key Features
- **Structured Extraction:** Uses `Instructor` and `Pydantic` to force LLM output into a strict, predictable JSON schema.
- **Action Item Tracking:** Automatically identifies tasks, assigns owners, and categorizes priority levels.
- **Sentiment Analysis:** Detects the meeting's emotional tone and overall mood.
- **Secure by Design:** Implements industry-standard `.env` environment variables to protect sensitive API credentials.

## 🛠 Tech Stack
- **Language:** Python 3.9+
- **LLM API:** Google Gemini 3 Flash
- **Data Validation:** Pydantic (v2)
- **AI Orchestration:** Instructor
- **Security:** `python-dotenv`

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed. It is highly recommended to use a virtual environment.

```powershell
# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Mac/Linux
2. Installation
Install the necessary dependencies using pip:

PowerShell
pip install instructor pydantic google-genai python-dotenv
3. Configuration (Security Setup)
To keep your API keys safe, this project uses environment variables.

Create a file named .env in the project root.

Add your Google API Key inside the file:

Plaintext
GEMINI_API_KEY=your_actual_api_key_here
Ensure your .gitignore file includes .env to prevent accidental leaks.

4. Running the Script
Execute the extractor to process your meeting transcript:

PowerShell
python extractor.py
📂 Project Structure
Plaintext
.
├── 01_meeting_minutes/
│   ├── extractor.py    # AI logic and prompt engineering
│   ├── schema.py       # Pydantic models for structured output
│   └── transcript.txt  # Input data (optional)
├── .env                # Local secrets (Never committed to Git)
├── .gitignore          # File exclusion rules
└── README.md           # Documentation
🛡 Security Note
This project was built with a "Security First" mindset. If you accidentally push an API key, remember to revoke the key immediately in Google AI Studio and rotate your secrets.

Developed by [Makarand Thorat] as part of the 2026 AI Engineering Portfolio.
