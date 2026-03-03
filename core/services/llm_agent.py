import os
import json
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import AsyncOpenAI, RateLimitError
from mcp import ClientSession
from dotenv import load_dotenv


# 1. Calculate absolute path to mcp_server.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVER_PATH = os.path.join(BASE_DIR, "mcp_server.py")

# 2. Define the correct MCP params exactly ONCE
server_params = StdioServerParameters(
    command=sys.executable,
    args=[SERVER_PATH], 
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

    # Prepare messages
    messages = [
        {"role": "system", "content": "You are CyberGuard, a helpful assistant for the elderly. Speak simply. If the user asks about a previous link or provides an image, use the context provided to help them."}
    ]
    messages.extend(history[-6:]) 

    # Handle Text and Images
    content_payload = []
    if user_input:
        content_payload.append({"type": "text", "text": user_input})
    if image_b64:
        content_payload.append({
            "type": "image_url",
            "image_url": {"url": image_b64}
        })

    messages.append({"role": "user", "content": content_payload})

    # === DUPLICATE SERVER_PARAMS HAS BEEN DELETED FROM HERE ===

    try:
        # Use AsyncOpenAI as an "async with" context manager
        async with AsyncOpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=api_key,
        ) as client:
            
            # This now uses the correct server_params from the top of the file!
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
                            
                            result_text = "".join([c.text for c in result.content if hasattr(c, "text")])

                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_call.function.name,
                                "content": result_text
                            })
    except Exception as e:
        import traceback
        traceback.print_exc() # Keep this so you can still see errors in the terminal
        
        # We use repr(e) to look inside the "ExceptionGroup" bubble
        error_details = repr(e)
        
        # If the Rate Limit error is hiding inside the bubble, show our friendly UI!
        if "RateLimitError" in error_details or "429" in error_details:
            return (
                "🛡️ **System Alert: Daily Limit Reached**\n\n"
                "I have reached my maximum number of free security scans for today. "
                "To keep this service free, I am limited to a certain number of deep AI analyses per day.\n\n"
                "**How to fix this:**\n"
                "* Please wait until tomorrow when my limits reset.\n"
                "* Or, update the `GITHUB_TOKEN` in your `.env` file with a fresh account."
            )
            
        # If it's a completely different error, show the standard fallback
        return f"System Error: {str(e)}"