# CyberGuard Architecture

## System Flow Diagram

```
┌─────────────┐
│   Browser   │
│  (User UI)  │
└──────┬──────┘
       │ HTTP POST /api/analyze/
       │ {"input": "Check this link: https://..."}
       ▼
┌─────────────────────────────────┐
│     Django (Async View)         │
│   core/views.py::analyze_risk   │
└───────────┬─────────────────────┘
            │ Calls run_analysis()
            ▼
┌─────────────────────────────────────────────┐
│        MCP Client / LLM Agent               │
│     core/services/llm_agent.py              │
│                                             │
│  1. Launch MCP Server (subprocess)          │
│  2. Connect via stdio                       │
│  3. Discover tools                          │
│  4. Convert to Claude format                │
└────────┬──────────────────┬─────────────────┘
         │                  │
         │ Tool Discovery   │ Tool Execution
         │ (async)          │ (async)
         ▼                  ▼
┌────────────────────┐   ┌─────────────────────┐
│   MCP Server       │   │  Claude AI API      │
│   mcp_server.py    │◄──┤  (Anthropic)        │
│                    │   │                     │
│  Tools:            │   │  Decides when to    │
│  - scan_url_...    │   │  call tools         │
└─────┬──────────────┘   └─────────────────────┘
      │
      │ VirusTotal API Call
      ▼
┌─────────────────────┐
│   VirusTotal API    │
│   (URL Scanning)    │
└─────────────────────┘
```

## Data Flow

### Step 1: User Input
```
User types: "Is this link safe? https://suspicious-site.com"
Frontend sends to: POST /api/analyze/
```

### Step 2: Django View (Async)
```python
async def analyze_risk(request):
    user_input = json.loads(request.body)['input']
    result = await run_analysis(user_input)
    return JsonResponse({'analysis': result})
```

### Step 3: MCP Client Initialization
```python
# Launch MCP server as subprocess
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Discover tools
        tools = await session.list_tools()
```

### Step 4: Tool Discovery
MCP Server exposes:
```python
{
    "name": "scan_url_reputation",
    "description": "Scan a URL's reputation using VirusTotal",
    "inputSchema": {
        "type": "object",
        "properties": {
            "url": {"type": "string"}
        }
    }
}
```

### Step 5: Claude Analysis
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    tools=claude_tools,  # Converted from MCP tools
    messages=[{
        "role": "user",
        "content": "Analyze: Is this link safe? https://..."
    }]
)
```

### Step 6: Claude Decides to Use Tool
Claude's response contains:
```json
{
    "type": "tool_use",
    "name": "scan_url_reputation",
    "input": {"url": "https://suspicious-site.com"}
}
```

### Step 7: Tool Execution via MCP
```python
result = await session.call_tool(
    "scan_url_reputation",
    {"url": "https://suspicious-site.com"}
)
```

### Step 8: MCP Server Calls VirusTotal
```python
# In mcp_server.py
url_id = base64.urlsafe_b64encode(url.encode())
response = requests.get(
    f"https://www.virustotal.com/api/v3/urls/{url_id}",
    headers={"x-apikey": VIRUSTOTAL_API_KEY}
)
```

### Step 9: VirusTotal Response
```json
{
    "data": {
        "attributes": {
            "last_analysis_stats": {
                "malicious": 15,
                "suspicious": 3,
                "harmless": 0
            }
        }
    }
}
```

### Step 10: MCP Server Returns Result
```
"⚠️ MALICIOUS: 15/89 security vendors flagged this URL as dangerous. DO NOT VISIT!"
```

### Step 11: Claude Synthesizes Final Response
```python
# Claude receives tool result and generates final response
messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": "...",
        "content": "⚠️ MALICIOUS: 15/89..."
    }]
})

final_response = client.messages.create(...)
```

Claude's final output:
```
I checked that link using security databases. 

❌ DO NOT CLICK THIS LINK!

15 out of 89 security companies say this website is dangerous. 
It could steal your personal information or install harmful software.

✅ What to do:
- Delete this message
- Don't click the link
- If someone sent this, let them know it's dangerous

Stay safe! 🛡️
```

## Key Technical Concepts

### 1. MCP Server (Tool Provider)
- Runs as separate process
- Exposes tools via stdio
- Handles actual API calls (VirusTotal)
- Stateless and reusable

### 2. MCP Client (Tool Consumer)
- Connects to MCP server
- Discovers available tools
- Translates for Claude API
- Executes tools on demand

### 3. Async Pattern
- Django uses async views
- MCP operations are async
- Non-blocking I/O throughout

### 4. Agentic Loop
```python
while True:
    response = claude.create(tools=tools, messages=messages)
    
    if no_tool_use:
        return final_answer
    
    tool_result = execute_tool(response.tool_use)
    messages.append(tool_result)
    # Loop continues...
```

## Why This Architecture?

### Separation of Concerns
- **MCP Server**: Tool implementation
- **MCP Client**: Tool orchestration  
- **Django**: HTTP interface
- **Claude**: Decision making

### Reusability
The MCP server can be used by:
- Other AI agents
- Different frontend applications
- CLI tools
- Multiple concurrent clients

### Scalability
- Stateless MCP server
- Async operations
- Independent tool scaling

### Security
- API keys isolated in server
- Tool execution sandboxed
- Clear permission boundaries

## File Responsibilities

### mcp_server.py
- **Purpose**: Provide security tools
- **Exports**: `scan_url_reputation(url)`
- **Dependencies**: VirusTotal API
- **Runtime**: Subprocess (stdio)

### llm_agent.py
- **Purpose**: Orchestrate AI + tools
- **Responsibilities**:
  - Launch MCP server
  - Connect Claude to tools
  - Manage conversation flow
- **Pattern**: Async client

### views.py
- **Purpose**: HTTP endpoints
- **Pattern**: Async views
- **Responsibility**: Request/response

### index.html
- **Purpose**: User interface
- **Features**: Fetch API, async/await
- **Design**: Elderly-friendly

## Extension Points

### Adding New Tools
```python
# In mcp_server.py
@mcp.tool()
def check_email_authenticity(email_content: str) -> str:
    """Check if email is phishing"""
    # Implementation
    return result
```

### Adding New Models
```python
# In llm_agent.py
response = client.messages.create(
    model="claude-opus-4-20250514",  # Switch model
    ...
)
```

### Adding Authentication
```python
# In views.py
from django.contrib.auth.decorators import login_required

@login_required
async def analyze_risk(request):
    ...
```

## Performance Characteristics

- **MCP Server Startup**: ~100-200ms
- **Tool Discovery**: ~50ms
- **Claude API Call**: ~1-3s
- **VirusTotal API**: ~500-1000ms
- **Total Request**: ~2-5s

## Error Handling

### Network Errors
```python
try:
    response = requests.get(url, timeout=10)
except requests.RequestException as e:
    return f"Network error: {str(e)}"
```

### API Errors
```python
if response.status_code != 200:
    return f"API error: {response.status_code}"
```

### MCP Errors
```python
try:
    async with ClientSession(...) as session:
        ...
except Exception as e:
    return f"Tool error: {str(e)}"
```
