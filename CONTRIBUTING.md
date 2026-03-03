## 🏗️ Understanding Our Architecture (Hybrid MVT)

While this is a Django project, we do **not** use the traditional database Model. Instead, we use a **Hybrid MVT (Model-View-Template)** architecture:

1. **The "Model" (Data Layer) ➔ The Agent & MCP:**
   Instead of a local SQL database, our data layer is dynamic. It consists of an AI Agent (`llm_agent.py`) and a Model Context Protocol server (`mcp_server.py`). The MCP server fetches real-time data from external APIs (like VirusTotal).
2. **The "View" (Controller) ➔ `core/views.py`:**
   Our Django views act as asynchronous traffic controllers. They receive the user's text, pass it to the AI Agent, and return the AI's JSON response.
3. **The "Template" (Presentation) ➔ `index.html`:**
   Our frontend acts like a lightweight Single Page Application (SPA). It uses JavaScript `fetch()` calls to talk to the backend without reloading the page, ensuring a smooth experience for our users.

---

## 🚀 Getting Started

Before you write code, ensure your local environment is set up:

1. **Activate the Virtual Environment:**
   - Windows: `.\venv\Scripts\Activate`
   - Mac/Linux: `source venv/bin/activate`
2. **Check your `.env` file:** Ensure you have your `GITHUB_TOKEN` (for the OpenAI API) and `VIRUSTOTAL_API_KEY` configured.
3. **Run the Setup Test:**
   Verify your environment by running `python test_setup.py`.

---

## 🛠️ How to Add a New Security Tool

The core of this project is expanding what the AI can check. Because we use the **Model Context Protocol (MCP)**, adding a new tool is incredibly easy. You only need to touch the server file!

### Step 1: Write the Tool in `mcp_server.py`

Open `mcp_server.py`. You will see our existing tools wrapped in the `@mcp.tool()` decorator. To add a new tool (e.g., checking if an email address is known for spam), just write a standard Python function and add the decorator.

**Crucial:** You *must* include a detailed docstring and type hints. The AI reads this docstring to understand how and when to use your tool!

```python
# mcp_server.py

@mcp.tool()
def check_email_spam_reputation(email_address: str) -> str:
    """
    Checks if an email address has been reported as a known spammer or scammer.
    Use this tool whenever the user asks about a specific email address.
    """
    print(f"--- [MCP SERVER] Checking email: {email_address} ---")
    
    # 1. Add your API call here (e.g., to HaveIBeenPwned, Hunter.io, etc.)
    # 2. Return the result as a string (JSON strings work best)
    
    if "scam" in email_address:
        return '{"status": "dangerous", "reports": 54, "reason": "Known phishing sender"}'
    
    return '{"status": "safe", "reports": 0}'
```

### Step 2: Update the System Prompt (Optional but Recommended)

The AI will automatically discover your new tool when the server starts. However, it helps to update the AI's instructions so it knows how to communicate the results to the user.

Open `core/services/llm_agent.py` and modify the `system_prompt`:

```python
system_prompt = """You are CyberGuard, a friendly cybersecurity assistant designed for elderly users.
                
Your role:
1. Analyze messages for potential scams, phishing, or suspicious URLs
2. When you find a URL, ALWAYS use the scan_url_reputation tool
3. If the user provides an email address, ALWAYS use the check_email_spam_reputation tool  <-- ADDED THIS
4. Explain security threats in simple, non-technical language..."""
```

### Step 3: Test Your Tool

1. Start the Django server: `python manage.py runserver`
2. Open `http://localhost:8000`
3. Type a prompt that triggers your new tool: *"I got an email from scammer@badguy.com, is it safe?"*
4. Watch the terminal! You should see your MCP server print `--- [MCP SERVER] Checking email...` which proves the AI successfully routed the request to your new Python function.

---

## 🎨 Frontend Changes

If your new feature requires UI changes (e.g., adding a new button or a file upload for analyzing scam PDFs):

1. Edit `core/templates/index.html`.
2. Keep the design **elderly-friendly**:
   - Use large, legible fonts.
   - Ensure high contrast.
   - Avoid overly technical jargon in the UI.
3. Update the JavaScript `fetch` call inside the `<script>` tag if you need to send different data formats to the backend.