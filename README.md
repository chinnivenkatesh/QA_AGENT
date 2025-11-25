
# 🤖 Autonomous QA Agent

An intelligent, autonomous QA agent capable of constructing a "testing brain" from project documentation. This system ingests support documents and HTML, generates comprehensive test cases using a local LLM (Ollama), and produces executable Selenium Python scripts for automated testing.

## 📋 Table of Contents

  - [Features](https://www.google.com/search?q=%23-features)
  - [Prerequisites](https://www.google.com/search?q=%23-prerequisites)
  - [Installation & Setup](https://www.google.com/search?q=%23-installation--setup)
  - [How to Run](https://www.google.com/search?q=%23-how-to-run)
  - [Usage Guide](https://www.google.com/search?q=%23-usage-guide)
  - [Project Structure](https://www.google.com/search?q=%23-project-structure)
  - [Included Assets](https://www.google.com/search?q=%23-included-assets)

-----

## ✨ Features

  * **Phase 1: Knowledge Base Ingestion:** Ingests and chunks documentation (PDF, MD, JSON, TXT) and HTML source code into a FAISS vector database.
  * **Phase 2: Autonomous Test Case Generation:** Uses a local LLM (Llama 3 via Ollama) to generate structured, documentation-grounded test plans.
  * **Phase 3: Automated Script Generation:** Converts selected test cases into fully executable Selenium WebDriver (Python) scripts based on the actual HTML selectors.
  * **Stack:** Python 3.11+, Flask (Backend), Waitress (Production Server), Streamlit (Frontend), LangChain, FAISS, Ollama.

-----

## ⚙️ Prerequisites

1.  **Python 3.11+**: Ensure Python is installed and added to your system PATH.
2.  **Ollama**: You must have [Ollama](https://ollama.com/) installed and running locally to power the AI agent.

-----

## 🛠️ Installation & Setup

### 1\. Clone the Repository

```bash
git clone https://github.com/chinnivenkatesh/QA_AGENT.git
cd QA_AGENT
```

### 2\. Set Up Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4\. Configure Local AI Model (Ollama)

Ensure Ollama is running in the background, then pull the required model.

```bash
# Pull the Llama 3 model (Recommended)
ollama pull llama3

# OR Pull TinyLlama (If you have low RAM < 4GB)
ollama pull tinyllama
```

### 5\. Configuration (.env)

Create a `.env` file in the root directory with the following settings:

```env
OLLAMA_BASE_URL="http://localhost:XXXX"
OLLAMA_MODEL="llama3" 
# Change to "tinyllama" if using the smaller model
EMBEDDING_MODEL_NAME="all-MiniLM-L6-v2"
```

-----

## 🚀 How to Run

The system requires two separate terminals to run the Backend (API) and Frontend (UI) simultaneously.

### Terminal 1: Start the Backend API

This starts the Flask server using Waitress (production-ready for Windows).

```bash
# Ensure venv is active
python -m waitress --listen=127.0.0.1:5000 src.backend:app
```

*You should see: `INFO:waitress:Serving on http://127.0.0.1:5000`*

### Terminal 2: Start the Frontend UI

This launches the Streamlit interface in your browser.

```bash
# Ensure venv is active
streamlit run app.py
```

*The app will open automatically at `http://localhost:8501`.*

-----

## 📖 Usage Guide

### Phase 1: Build the "Testing Brain"

1.  Go to the **Knowledge Base Ingestion** section.
2.  Upload your **Support Documents** (`product_specs.md`, `ui_ux_guide.txt`, etc.).
3.  Upload your **Target HTML** (`checkout.html`).
4.  Click **"Build Knowledge Base"**.
      * *Result:* The system chunks the text, creates embeddings, and saves a FAISS index locally.

### Phase 2: Generate Test Cases

1.  Enter a prompt (e.g., *"Generate positive and negative test cases for the discount code feature"*).
2.  Click **"Generate Test Cases"**.
      * *Result:* The agent retrieves relevant rules from the vector DB and uses the local LLM to generate a structured test plan table.

### Phase 3: Generate Automation Script

1.  Select one of the generated test cases from the dropdown menu.
2.  Click **"Generate Selenium Script"**.
      * *Result:* The agent writes a complete, runnable Python script using `unittest` and `selenium`, with selectors extracted directly from your uploaded HTML.

-----

## 📂 Included Assets (Support Documents)

The `assets/` folder contains sample files used to demonstrate the agent's capabilities:

1.  **`checkout.html`**: The target web page. It contains the specific IDs (e.g., `#discount-code-input`) and structure the agent must analyze to write code.
2.  **`product_specs.md`**: Defines the functional logic.
      * *Example Rule:* "The code SAVE15 gives a 15% discount." (The agent uses this to verify expected results).
3.  **`ui_ux_guide.txt`**: Defines visual requirements.
      * *Example Rule:* "Error messages must be red." (The agent uses this for UI assertions).
4.  **`api_endpoints.json`**: Provides context on backend API structures for integration testing.

-----

## 🏗️ Project Structure

```
qa-agent-project/
├── app.py                  # Streamlit Frontend UI
├── requirements.txt        # Python dependencies
├── .env                    # Configuration variables
├── src/
│   ├── backend.py          # Flask API Server
│   ├── knowledge_base.py   # Vector DB (FAISS) & Ingestion Logic
│   ├── agent_test_case.py  # LLM Agent for Test Case Generation
│   └── agent_script_gen.py # LLM Agent for Selenium Script Writing
└── assets/                 # Sample testing documents
```
