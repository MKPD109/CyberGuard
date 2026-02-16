# CyberGuard - AI-Powered Security Assistant for Elderly Users

A full-stack cybersecurity web application that uses Claude AI with Model Context Protocol (MCP) to analyze messages and URLs for potential threats.

## 🏗️ Architecture

This project demonstrates a **proper MCP implementation** with:

1. **MCP Server** (`mcp_server.py`) - Standalone tool server providing VirusTotal URL scanning
2. **MCP Client** (`core/services/llm_agent.py`) - Agent orchestrating Claude with MCP tools
3. **Django Backend** - Async views handling API requests
4. **Simple Frontend** - Elderly-friendly interface

## 📋 Prerequisites

- Python 3.11 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))
- VirusTotal API key ([get one here](https://www.virustotal.com/gui/my-apikey))

## 🚀 Installation

### 1. Install Dependencies

```bash
cd cyberguard_project
pip install -r requirements.txt
```

Or manually:
```bash
pip install django>=5.0.0 anthropic>=0.39.0 mcp[cli]>=1.0.0 requests>=2.32.0 python-dotenv>=1.0.0
```

### 2. Configure API Keys

Edit the `.env` file and add your API keys:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
VIRUSTOTAL_API_KEY=your-virustotal-key-here
```

### 3. Test the MCP Server (Optional)

Verify the MCP server works:

```bash
python mcp_server.py
```

You should see the MCP server start. Press Ctrl+C to stop.

## 🎯 Usage

### Start the Application

```bash
python manage.py runserver
```

### Access the Interface

Open your browser to: **http://localhost:8000**

### Test the Application

Try these examples:

1. **Safe URL Test:**
   ```
   Check this link: https://www.google.com
   ```

2. **Suspicious Message Test:**
   ```
   You won $1,000,000! Click here to claim: http://suspicious-site.xyz/prize
   ```

3. **Email Analysis:**
   ```
   I got this email from "Microsoft" saying my account will be closed. 
   Click here immediately: https://micros0ft-security.com/verify
   ```

## 🔧 How It Works

### 1. User Submits Input
The frontend sends user text to `/api/analyze/`

### 2. MCP Client Launches
Django view calls `run_analysis()` which:
- Spawns the MCP server as a subprocess
- Connects via stdio transport
- Discovers available tools

### 3. Claude Analyzes
The agent sends user input + tool definitions to Claude:
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    system="You are CyberGuard...",
    tools=claude_tools,
    messages=[{"role": "user", "content": user_input}]
)
```

### 4. Tool Execution (if needed)
If Claude detects a URL, it calls `scan_url_reputation`:
```python
tool_result = await session.call_tool(
    "scan_url_reputation", 
    {"url": "https://example.com"}
)
```

### 5. Final Response
Claude synthesizes the tool results into elderly-friendly advice.

## 📁 Project Structure

```
cyberguard_project/
├── manage.py                    # Django management
├── requirements.txt             # Python dependencies
├── .env                         # API keys (YOU MUST EDIT THIS)
├── mcp_server.py               # MCP tool server (VirusTotal)
├── cyberguard_project/
│   ├── __init__.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # URL routing
│   └── wsgi.py                 # WSGI config
└── core/
    ├── __init__.py
    ├── views.py                # Async API views
    ├── urls.py                 # App URLs
    ├── services/
    │   ├── __init__.py
    │   └── llm_agent.py        # MCP client + Claude orchestration
    └── templates/
        └── index.html          # Frontend interface
```

## 🎨 Features

- ✅ **True MCP Architecture** - Proper client-server separation
- ✅ **Async Django Views** - Non-blocking request handling
- ✅ **Elderly-Friendly UI** - Large text, high contrast, simple language
- ✅ **Real VirusTotal Integration** - Actual URL reputation checking
- ✅ **Agentic Tool Use** - Claude decides when to scan URLs
- ✅ **Graceful Error Handling** - User-friendly error messages

## 🔐 Security Notes

- Never commit API keys to version control
- The `.env` file is gitignored by default
- Use HTTPS in production
- Add rate limiting for production deployments

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "API key not configured"
Edit `.env` file with your actual keys

### MCP server errors
Check that Python is in your PATH:
```bash
python --version
```

### Port 8000 already in use
```bash
python manage.py runserver 8080
```

## 📚 Learning Resources

- [Anthropic MCP Documentation](https://docs.anthropic.com/mcp)
- [Claude API Docs](https://docs.anthropic.com/claude/reference)
- [VirusTotal API](https://developers.virustotal.com/reference/overview)

## 🎓 Key Concepts Demonstrated

1. **MCP Server Development** - Creating custom tool servers
2. **MCP Client Integration** - Connecting to tool servers
3. **Async Python** - Proper async/await patterns
4. **Agentic AI** - Multi-turn tool use
5. **Django Async Views** - Modern Django patterns
6. **User-Centric Design** - Accessibility for elderly users

## 📝 License

This is a prototype for educational purposes.

## 🤝 Contributing

This is a learning project demonstrating MCP architecture patterns.

---

**Built with ❤️ for safer internet experiences**
