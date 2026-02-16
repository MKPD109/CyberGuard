"""
LLM Agent Service - MCP Client for CyberGuard
Orchestrates Claude AI with MCP tool server
"""
import os
import asyncio
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def run_analysis(user_input: str) -> str:
    """
    Analyze user input for cybersecurity threats using Claude + MCP tools.
    
    Args:
        user_input: The text/URL submitted by the user
    
    Returns:
        Analysis result from Claude
    """
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "Error: Anthropic API key not configured"
    
    # Initialize Anthropic client
    client = Anthropic(api_key=api_key)
    
    # MCP server parameters - launch our tool server as subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=None
    )
    
    try:
        # Connect to MCP server via stdio
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                # Discover available tools from MCP server
                tools_list = await session.list_tools()
                
                # Convert MCP tools to Claude's tool format
                claude_tools = []
                for tool in tools_list.tools:
                    claude_tool = {
                        "name": tool.name,
                        "description": tool.description or "",
                        "input_schema": tool.inputSchema
                    }
                    claude_tools.append(claude_tool)
                
                # System prompt for elderly-friendly security analysis
                system_prompt = """You are CyberGuard, a friendly cybersecurity assistant designed for elderly users.

Your role:
1. Analyze messages for potential scams, phishing, or suspicious URLs
2. When you find a URL, ALWAYS use the scan_url_reputation tool to check it
3. Explain security threats in simple, non-technical language
4. Give clear YES/NO advice on whether something is safe

Communication style:
- Use simple words (avoid jargon like "phishing", "malware" - explain what they do)
- Be warm and reassuring, not scary
- Give actionable advice
- Use emojis sparingly for clarity (✅ ❌ ⚠️)

Always prioritize user safety over convenience."""
                
                # Initial message to Claude
                messages = [
                    {
                        "role": "user",
                        "content": f"Please analyze this message for security threats:\n\n{user_input}"
                    }
                ]
                
                # Agentic loop - Claude can use tools iteratively
                while True:
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1000,
                        system=system_prompt,
                        tools=claude_tools,
                        messages=messages
                    )
                    
                    # Check if Claude wants to use a tool
                    tool_use_block = None
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_use_block = block
                            break
                    
                    if not tool_use_block:
                        # No tool use - Claude has final answer
                        final_text = ""
                        for block in response.content:
                            if hasattr(block, "text"):
                                final_text += block.text
                        return final_text or "Analysis complete."
                    
                    # Claude wants to use a tool
                    tool_name = tool_use_block.name
                    tool_input = tool_use_block.input
                    
                    # Execute the tool via MCP
                    tool_result = await session.call_tool(tool_name, tool_input)
                    
                    # Extract result content
                    result_text = ""
                    for content in tool_result.content:
                        if hasattr(content, "text"):
                            result_text += content.text
                    
                    # Add Claude's response to conversation
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    
                    # Add tool result to conversation
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_block.id,
                                "content": result_text
                            }
                        ]
                    })
                    
                    # Loop continues - Claude will process tool result
    
    except Exception as e:
        return f"Error during analysis: {str(e)}"


# Synchronous wrapper for Django views
def analyze_user_input(user_input: str) -> str:
    """
    Synchronous wrapper for run_analysis.
    """
    return asyncio.run(run_analysis(user_input))
