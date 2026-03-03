import os
import json
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# 1. Calculate the absolute path to the root of your project
# (This goes up a few folders from llm_agent.py to find the main directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 2. Point exactly to your mcp_server.py file
# IMPORTANT: If your mcp_server.py is inside core/services/, change "mcp_server.py" below to "core/services/mcp_server.py"
SERVER_PATH = os.path.join(BASE_DIR, "mcp_server.py")

# 3. Use sys.executable and the absolute SERVER_PATH
server_params = StdioServerParameters(
    command=sys.executable,
    args=[SERVER_PATH], 
    # Optional but highly recommended: pass your environment variables down so the server has them
    env=os.environ.copy() 
)

# Load environment variables
load_dotenv()

async def run_analysis(user_input: str, history: list = None, image_b64: str = None) -> str:
    """
    Analyzes text and images with context. 
    """
    if history is None:
        history = []
        
    api_key = os.getenv("GITHUB_TOKEN")
    
    if not api_key:
        return "Error: GITHUB_TOKEN not found in environment variables."

    # 1. Prepare the messages list
    messages = [
        {"role": "system", "content": "You are CyberGuard, a helpful assistant for the elderly. Speak simply. If the user asks about a previous link or provides an image, use the context provided to help them."}
    ]
    messages.extend(history[-6:]) 

    # 2. Format the CURRENT user message to handle both Text and Images
    content_payload = []
    
    if user_input:
        content_payload.append({"type": "text", "text": user_input})
        
    if image_b64:
        content_payload.append({
            "type": "image_url",
            "image_url": {"url": image_b64}
        })

    messages.append({"role": "user", "content": content_payload})

    # MCP server parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
        env=None
    )

    try:
        # FIX: We now use AsyncOpenAI as an "async with" context manager!
        # This guarantees it closes its network connections safely before returning.
        async with AsyncOpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=api_key,
        ) as client:
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Discover tools dynamically from MCP
                    tools_list = await session.list_tools()
                    openai_tools = [
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description or "",
                                "parameters": tool.inputSchema
                            }
                        } for tool in tools_list.tools
                    ]

                    # Agent Loop
                    while True:
                        response = await client.chat.completions.create(
                            model="gpt-4o",
                            messages=messages,
                            tools=openai_tools if openai_tools else None,
                            tool_choice="auto"
                        )

                        response_message = response.choices[0].message
                        if not response_message.tool_calls:
                            return response_message.content

                        messages.append(response_message)

                        for tool_call in response_message.tool_calls:
                            result = await session.call_tool(
                                tool_call.function.name, 
                                json.loads(tool_call.function.arguments)
                            )
                            
                            # Extract the text from MCP result
                            result_text = "".join([c.text for c in result.content if hasattr(c, "text")])

                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_call.function.name,
                                "content": result_text
                            })
    except Exception as e:
        return f"System Error: {str(e)}"