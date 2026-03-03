# CyberGuard - AI-Powered Security Assistant (GitHub Models Edition)

A full-stack cybersecurity web application that uses **GitHub Models API (GPT-4)** with **Model Context Protocol (MCP)** to analyze GitHub repositories and messages for security threats.

## 🏗️ Architecture

This project demonstrates a **proper MCP implementation** with:

1. **MCP Server** (`mcp_server.py`) - Standalone tool server providing GitHub repository security analysis
2. **MCP Client** (`core/services/llm_agent.py`) - Agent orchestrating GPT-4 (via GitHub Models) with MCP tools
3. **Django Backend** - Async views handling API requests
4. **Simple Frontend** - Elderly-friendly interface

## 🌟 What is GitHub Models?

GitHub Models provides **free access to GPT-4** through GitHub's Azure-hosted infrastructure. No credit card required!

**Key Benefits:**
- 🆓 **Free Tier** - 15 requests per minute
- 🔐 **Fine-Grained Tokens** - Enhanced security with granular permissions
- ⚡ **Azure Infrastructure** - Reliable, fast GPT-4 hosting
- 🛠️ **GitHub Integration** - Unified authentication for AI + repo analysis

## 📋 Prerequisites

- Python 3.11 or higher
- GitHub Fine-Grained Personal Access Token ([get one here](https://github.com/settings/tokens?type=beta))
- Access to GitHub Models (free tier available)

## 🚀 Installation

### 1. Install Dependencies

```bash
cd cyberguard_project
pip install -r requirements.txt
```

Or manually:
```bash
pip install django>=5.0.0 openai>=1.12.0 mcp[cli]>=1.0.0 requests>=2.32.0 python-dotenv>=1.0.0
```

### 2. Get GitHub Fine-Grained Token

**Step-by-Step:**

1. **Visit Token Settings:**
   - Go to: https://github.com/settings/tokens?type=beta
   - You'll see "Fine-grained tokens" page

2. **Generate New Token:**
   - Click "Generate new token (fine-grained)"
   
3. **Configure Token:**
   ```
   Token name: CyberGuard-MCP
   Expiration: 90 days (recommended)
   Description: Token for CyberGuard security app
   ```

4. **Set Permissions:**
   Under "Account permissions":
   - ✅ `model:read` - **Required** (read access to models)
   - ✅ `model:write` - **Required** (use GitHub Models API)
   - Optional: `public_repo` - For analyzing public repositories

5. **Generate & Copy:**
   - Click green "Generate token" button
   - **COPY IMMEDIATELY** (starts with `github_pat_`)
   - You won't see it again!

### 3. Configure Environment

Edit the `.env` file:

```env
GITHUB_TOKEN=github_pat_your-fine-grained-token-here
GITHUB_ENDPOINT=https://models.inference.ai.azure.com
```

**Important Notes:**
- Token **must** start with `github_pat_` (Fine-Grained format)
- Classic tokens (`ghp_` or `gho_`) will **not** work
- Endpoint is GitHub's Azure-hosted model service

### 4. Test the Setup

```bash
python test_setup.py
```

Expected output:
```
✓ GITHUB_TOKEN: github_pat_11... (Fine-Grained)
✓ GITHUB_ENDPOINT: https://models.inference.ai.azure.com
✓ MCP server imports work
✅ Setup looks good!
```

## 🎯 Usage

### Start the Application

```bash
python manage.py runserver
```

### Access the Interface

Open your browser to: **http://localhost:8000**

### Test the Application

Try these examples:

1. **Popular Repository Check:**
   ```
   Is this repository safe? https://github.com/microsoft/vscode
   ```
   Expected: ✅ Safe - well-known Microsoft project with high trust

2. **New Repository Warning:**
   ```
   Someone sent me this: https://github.com/new-user-123/free-crypto-bot
   ```
   Expected: ⚠️ Warning - new account, low activity, suspicious name

3. **Suspicious Code Link:**
   ```
   Download this tool: https://github.com/random-dev/password-stealer
   ```
   Expected: 🚨 Strong warning with detailed security concerns

## 🔧 How It Works

### 1. User Submits Input
Frontend sends user text to `/api/analyze/`

### 2. MCP Client Launches
Django view calls `run_analysis()` which:
- Spawns the MCP server as a subprocess
- Connects via stdio transport
- Discovers available GitHub security tools

### 3. GPT-4 Analyzes (via GitHub Models)
Agent connects to GitHub's model endpoint:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"]  # Fine-Grained token
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": user_input}],
    tools=github_security_tools
)
```

### 4. Tool Execution (if needed)
If GPT-4 detects a GitHub URL, it calls `check_github_repo_safety`:

```python
tool_result = await session.call_tool(
    "check_github_repo_safety", 
    {"repo_url": "https://github.com/user/repo"}
)
```

### 5. GitHub Security Analysis
MCP server checks via GitHub API:
- ⭐ **Popularity** - Stars, forks, watchers count
- 📅 **Age & Maintenance** - Creation date, last update
- 🔒 **Security** - Vulnerability alerts, security advisories
- 🚨 **Exposed Secrets** - Secret scanning results
- ✅ **Legitimacy** - Overall safety assessment

### 6. Final Response
GPT-4 synthesizes the analysis into elderly-friendly advice.

## 📁 Project Structure

```
cyberguard_project/
├── manage.py                    # Django management
├── requirements.txt             # Python dependencies
├── .env                         # GitHub token & endpoint (EDIT THIS!)
├── mcp_server.py               # MCP tool server (GitHub security)
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
    │   └── llm_agent.py        # MCP client + GPT-4 orchestration
    └── templates/
        └── index.html          # Frontend interface
```

## 🎨 Features

- ✅ **GitHub Models API** - Free GPT-4 access via GitHub
- ✅ **Fine-Grained Tokens** - Enhanced security with granular permissions
- ✅ **MCP Architecture** - Proper client-server tool separation
- ✅ **Async Django Views** - Non-blocking request handling
- ✅ **Repository Safety Analysis** - Comprehensive GitHub security checks
- ✅ **Elderly-Friendly UI** - Large text, high contrast, simple language
- ✅ **Agentic Tool Use** - GPT-4 autonomously decides when to use tools
- ✅ **Graceful Error Handling** - User-friendly error messages

## 🛡️ GitHub Security Tools

### Tool 1: check_github_repo_safety
Comprehensive repository security analysis:
- **Popularity Metrics** - Stars, forks, watchers
- **Repository Age** - Creation date, time since last update
- **Maintenance Status** - Active vs archived
- **Community Trust** - Established vs new account
- **Safety Recommendation** - Clear guidance for users

### Tool 2: scan_for_exposed_secrets
Advanced security scanning:
- **Secret Scanning** - Exposed API keys, tokens
- **Vulnerability Alerts** - Known security issues
- **Security Advisories** - Published vulnerabilities
- **Risk Assessment** - Overall security posture

## 🔐 Security Notes

### Fine-Grained Token Security

**Why Fine-Grained Tokens are Better:**
| Feature | Classic Token | Fine-Grained Token |
|---------|---------------|-------------------|
| Format | `ghp_...` / `gho_...` | `github_pat_...` |
| Expiration | Optional | **Required** ✅ |
| Permissions | All-or-nothing | **Granular** ✅ |
| Repo Access | All repositories | **Specific repos** ✅ |
| Audit Trail | Limited | **Detailed** ✅ |
| Security | ⚠️ Less secure | ✅ **More secure** |

### Best Practices

1. **Token Management:**
   - ✅ Never commit tokens to version control
   - ✅ Store in `.env` file (gitignored)
   - ✅ Set expiration dates (90 days recommended)
   - ✅ Rotate tokens regularly
   - ✅ Revoke immediately if compromised

2. **Permission Principle:**
   - ✅ Grant **minimum required** permissions
   - ✅ Only enable `model:read` and `model:write`
   - ✅ Add repo permissions only if needed
   - ✅ Review permissions periodically

3. **Production Deployment:**
   - ✅ Use HTTPS only
   - ✅ Add rate limiting
   - ✅ Implement authentication
   - ✅ Monitor API usage
   - ✅ Set up error alerting

## 🐛 Troubleshooting

### "Unauthorized" or "Invalid token"
**Causes:**
- Token doesn't start with `github_pat_`
- Missing `model:read` or `model:write` permissions
- Token expired

**Solutions:**
1. Verify token format: `github_pat_...`
2. Check permissions at: https://github.com/settings/tokens
3. Regenerate if expired

### "Rate limit exceeded"
**Free Tier Limits:**
- GitHub Models: 15 requests/minute
- GitHub API: 5,000 requests/hour (with token)

**Solution:** Wait 1 minute for rate limit reset

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### MCP server errors
```bash
# Check Python is accessible
python --version

# Test MCP server directly
python mcp_server.py
```

### Port 8000 already in use
```bash
python manage.py runserver 8080
```

## 📊 GitHub Models API Details

### What is GitHub Models?
- **Azure-hosted AI models** accessible through GitHub
- **Free tier available** - No credit card required
- **Uses OpenAI SDK** - Familiar API format
- **GitHub authentication** - Fine-Grained tokens

### Available Models
```python
# Primary model (recommended)
model="gpt-4o"

# Alternative models
model="gpt-4-turbo"      # Fast, powerful
model="gpt-3.5-turbo"    # Fastest, economical
```

### API Endpoint
```python
Base URL: https://models.inference.ai.azure.com
Authentication: GitHub Fine-Grained Token
SDK: OpenAI Python SDK
```

### Rate Limits & Costs
**Free Tier:**
- 15 requests per minute
- Resets every minute
- Perfect for testing and development

**GitHub API:**
- 5,000 requests/hour (with token)
- 60 requests/hour (without token)

**Cost:** FREE with rate limits

## 📚 Learning Resources

### Official Documentation
- **GitHub Models:** https://github.com/marketplace/models
- **Fine-Grained Tokens:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- **MCP Protocol:** https://docs.anthropic.com/mcp
- **GitHub REST API:** https://docs.github.com/en/rest
- **Django Async:** https://docs.djangoproject.com/en/5.0/topics/async/

### Tutorials & Guides
- Creating Fine-Grained tokens
- Using GitHub Models API
- Building MCP tool servers
- Async Python patterns

## 🎓 Key Concepts Demonstrated

1. **GitHub Models Integration** - Azure-hosted GPT-4 via GitHub
2. **Fine-Grained Authentication** - Modern, secure token system
3. **MCP Server Development** - Custom tool server creation
4. **MCP Client Integration** - Tool discovery and execution
5. **Async Python** - Proper async/await patterns
6. **Agentic AI** - Multi-turn tool use and decision making
7. **Django Async Views** - Non-blocking web framework
8. **Repository Security Analysis** - GitHub API integration

## 💡 Extension Ideas

1. **Code Pattern Analysis** - Scan source code for malicious patterns
2. **Dependency Scanning** - Check package.json/requirements.txt vulnerabilities
3. **License Verification** - Analyze and verify software licenses
4. **Commit History Analysis** - Review contributor patterns and behavior
5. **Pull Request Security** - Automated security review of PRs
6. **Issue Tracking** - Monitor security-related issues
7. **Multi-language Support** - Internationalization for global users
8. **Mobile Application** - React Native or Flutter frontend

## 🔄 Switching Models

GitHub Models supports multiple AI models:

```python
# In core/services/llm_agent.py

# Latest GPT-4 (recommended)
model="gpt-4o"

# GPT-4 Turbo (faster)
model="gpt-4-turbo"

# GPT-3.5 (fastest, cheapest)
model="gpt-3.5-turbo"
```

## 📝 License

This is a prototype for educational purposes demonstrating:
- GitHub Models API integration
- Fine-grained token authentication
- MCP architecture patterns
- Repository security analysis

## 🤝 Contributing

This project showcases modern AI application patterns:
- Free-tier AI model access via GitHub
- Secure token-based authentication
- Microservice architecture with MCP
- Async Python web development

## 🎉 Why This Stack?

**GitHub Models:**
- 🆓 Free access to GPT-4
- 🔐 Secure Fine-Grained tokens
- ⚡ Azure infrastructure
- 🛠️ Easy GitHub integration

**MCP Architecture:**
- 🔧 Modular tool design
- 🔄 Reusable components
- 📊 Clear separation of concerns
- 🚀 Scalable pattern

**Django Async:**
- ⚡ Non-blocking operations
- 🎯 Modern Python patterns
- 📈 Production-ready framework
- 🔒 Built-in security features

---

**Built with ❤️ for safer code exploration using GitHub Models**

**Free Tier + Enterprise Security = Perfect for Learning! 🛡️**