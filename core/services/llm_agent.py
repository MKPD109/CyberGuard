import os
import json
import asyncio
from openai import AsyncOpenAI  # Use AsyncOpenAI for Django async views
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# Load environment variables at the top of the file
load_dotenv()

async def run_analysis(user_input: str, history: list = None) -> str:
    """
    Analyzes text with context. 
    'history' is a list of {"role": "user/assistant", "content": "..."}
    """
    
    if history is None:
        history = []
    # 1. Retrieve the token from environment variables
    # Ensure your .env file has: GITHUB_TOKEN=ghp_...
    api_key = os.getenv("GITHUB_TOKEN")
    
    if not api_key:
        return "Error: GITHUB_TOKEN not found in environment variables."

    # 2. Initialize the ASYNC client INSIDE the function to avoid startup crashes
    client = AsyncOpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=api_key,
    )

    # 1. Prepare the messages list
    # Start with the System Prompt
    messages = [
        {"role": "system", "content": "You are CyberGuard. Speak simply. If the user asks about a previous link, use the context provided."}
    ]
    
    # 2. Append the conversation history (Context)
    # We take the last 6 messages to keep it fast and cheap (Context Window)
    messages.extend(history[-6:]) 

    # 3. Add the CURRENT user message
    messages.append({"role": "user", "content": user_input})

    # MCP server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=None
    )

    try:
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

                messages = [
                    {"role": "system", "content": "You are CyberGuard, a helpful assistant for the elderly."},
                    {"role": "user", "content": f"Analyze this: {user_input}"}
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