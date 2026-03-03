# 🛡️ CyberGuard - AI-Powered Security Assistant

A full-stack cybersecurity web application designed to protect elderly and vulnerable users from digital scams. It uses **GitHub Models (GPT-4o)**, **MCP (Model Context Protocol)**, and a **Persistent Database** to provide contextual, image-aware security analysis in a user-friendly, ChatGPT-style interface.

## ✨ Key Features

### 👁️ Vision & Image Analysis
- **Screenshot Scanning:** Users can upload images of suspicious emails, text messages, or websites.
- **Instant Previews:** High-fidelity image thumbnails appear before sending, just like modern chat apps.
- **Inline Rendering:** Uploaded images are embedded directly into the chat history for a clear visual audit trail.
- **Token Optimization:** A smart backend filter strips massive image data from historical messages to protect API limits while maintaining context.

### 🧠 Persistent Memory & State
- **Database Integration:** Fully stateful architecture using a relational database to store sessions and messages.
- **Multi-Chat Management:** Users can maintain, switch between, and permanently delete different conversation tabs via a dedicated sidebar.
- **Contextual Awareness:** The AI remembers recent messages within a session to answer follow-up questions accurately.

### 🛠️ Advanced Security Tools (MCP)
The application uses a standalone Model Context Protocol (MCP) server to give the AI agent real-time security scanning capabilities without exposing the core logic:
- **DNS & Email Verification:** Automatically scans MX, SPF, and DMARC records to determine if an email sender is spoofed or fraudulent.
- **Repository Scanner:** Analyzes source code repositories for malicious patterns, new account warnings, and overall trust scores.

### 🎨 Modern UI/UX
- **ChatGPT-Style Layout:** A beautiful, full-screen responsive interface with a dark sidebar and light chat window.
- **Rich Text Formatting:** Integrates Markdown parsing to display bold text, bullet points, and numbered lists for highly readable security advice.
- **Elderly-Friendly:** Designed with large text, clear loading indicators, and simple language instructions.

## 🏗️ Architecture

1. **Django Backend:** Handles asynchronous API requests, database ORM, and file routing.
2. **MCP Server (`mcp_server.py`):** A standalone tool server providing specialized security scans (DNS, Repositories).
3. **MCP Client & Agent (`llm_agent.py`):** Orchestrates the OpenAI SDK, routing prompts and images to GitHub Models and triggering MCP tools when necessary.
4. **SQLite Database:** Provides zero-config, persistent storage for chat histories.

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python** installed on your system.
- A **GitHub Fine-Grained Personal Access Token** (Requires `model:read` and `model:write` permissions).

### 2. Environment Setup
Clone the repository and set up a virtual environment:
```bash
# Create and activate a virtual environment
python -m venv venv

# Windows Activation:
venv\Scripts\activate
# Mac/Linux Activation:
source venv/bin/activate


```

### 3. Install Dependencies

Install the required packages using pip:

```bash
pip install -r requirements.txt

```

*(If you do not have a requirements file, you will need: `django`, `openai`, `mcp[cli]`, `requests`, `python-dotenv`, `dnspython`, and `httpx`)*

### 4. Database Initialization

Build the local database for the persistent chat memory:

```bash
python manage.py makemigrations core
python manage.py migrate

```

### 5. Configure Environment Variables

Create a `.env` file in the root directory and add your GitHub token:

```env
GITHUB_TOKEN=github_pat_your_fine_grained_token_here
GITHUB_ENDPOINT=https://models.inference.ai.azure.com

```

---

## 🎯 Usage

### Verify the Installation

Run the included test script to ensure your environment, database, and DNS tools are linked correctly:

```bash
python test_setup.py

```

### Start the Application

Launch the Django development server:

```bash
python manage.py runserver

```

Open your browser and navigate to **http://localhost:8000** to start chatting!

### Example Scans to Try:

1. **Upload an Image:** Take a screenshot of a spam email, click the paperclip icon 📎 to upload it, and ask: *"Is this email safe?"*
2. **Test the DNS Tool:** *"I got an email from support@apple-security-alert-xyz.com, is this real?"*
3. **Test the Repo Tool:** *"Is the microsoft/vscode repository safe to download?"*

---

## 🔐 Security & Privacy Notes

* **Local Database:** All chat logs and image references are stored locally in your SQLite database, ensuring user privacy.
* **Token Management:** Never commit your `.env` file to version control. The application utilizes secure backend-to-backend calls so your API keys are never exposed to the frontend browser.
* **Cost Efficiency:** By utilizing GitHub Models' free tier and aggressively optimizing token usage (capping history length and stripping historical Base64 images), the application operates safely within API limits.

---

**Built to make the digital world a safer place for everyone. 🛡️**
