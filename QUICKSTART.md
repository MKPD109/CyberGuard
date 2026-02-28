# CyberGuard Quick Reference

## 🚀 Setup (5 Minutes)

### 1. Install Dependencies
```bash
cd cyberguard_project
pip install -r requirements.txt
```

### 2. Configure API Keys
Edit `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
VIRUSTOTAL_API_KEY=your-virustotal-key-here
```

Get keys:
- Anthropic: https://console.anthropic.com/
- VirusTotal: https://www.virustotal.com/gui/my-apikey

### 3. Test Setup
```bash
python test_setup.py
```

### 4. Run Application
```bash
python manage.py runserver
```

Open: http://localhost:8000

## 📝 Quick Test Examples

### Example 1: Safe URL
```
Check this website: https://www.google.com
```

Expected: ✅ Safe confirmation

### Example 2: Suspicious Message
```
URGENT! Your account will be closed! 
Click here: http://fake-bank-security.com/verify
```

Expected: ⚠️ Warning about phishing

### Example 3: Unknown Link
```
My friend sent me this: https://super-new-site-12345.xyz
```

Expected: Caution about unknown sites

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Run `pip install -r requirements.txt` |
| "API key not configured" | Edit `.env` with actual keys |
| Port 8000 in use | Run `python manage.py runserver 8080` |
| MCP server errors | Check Python is in PATH |
| Slow responses | Normal - Claude + VirusTotal take 2-5s |

## 📂 File Reference

| File | Purpose |
|------|---------|
| `mcp_server.py` | MCP tool server (VirusTotal) |
| `core/services/llm_agent.py` | MCP client + Claude orchestration |
| `core/views.py` | Django API endpoints |
| `core/templates/index.html` | Frontend UI |
| `.env` | API keys (EDIT THIS!) |

## 🔧 Common Commands

```bash
# Start server
python manage.py runserver

# Different port
python manage.py runserver 8080

# Test setup
python test_setup.py

# Install dependencies
pip install -r requirements.txt
```

## 🎯 How It Works (Simple)

1. **User types** message with URL
2. **Django** receives it
3. **MCP Client** launches tool server
4. **Claude** analyzes message
5. **Claude** calls scan_url_reputation tool
6. **MCP Server** checks VirusTotal
7. **Claude** explains result simply
8. **User** sees friendly advice

## 🔐 Security Best Practices

- ✅ Keep API keys in `.env` (never commit)
- ✅ Use HTTPS in production
- ✅ Add rate limiting
- ✅ Validate all inputs
- ✅ Update dependencies regularly

## 📚 Learn More

- MCP Docs: https://docs.anthropic.com/mcp
- Claude API: https://docs.anthropic.com/claude
- Django Async: https://docs.djangoproject.com/en/5.0/topics/async/

## 🎓 Key MCP Concepts

### MCP Server
- Runs independently
- Provides tools
- Stateless

### MCP Client  
- Connects to server
- Discovers tools
- Executes on demand

### Agentic Pattern
```
User → Claude → Tool → Claude → User
         ↓              ↑
      Decides      Executes
```

## 💡 Extension Ideas

1. **Add email scanning** - Detect phishing emails
2. **Phone number validation** - Check for scam calls
3. **Image analysis** - Scan suspicious QR codes
4. **Multi-language** - Support other languages
5. **Mobile app** - React Native frontend

## 🆘 Need Help?

1. Check README.md for detailed docs
2. Check ARCHITECTURE.md for system design
3. Run test_setup.py to verify configuration
4. Check Django debug logs for errors

---

**Remember: API keys must be in `.env` file!**
