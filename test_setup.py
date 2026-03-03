#!/usr/bin/env python
"""
Quick test script to verify CyberGuard setup (OpenAI/GitHub Edition)
"""
import os
import sys
from dotenv import load_dotenv

print("🔍 CyberGuard Setup Verification\n")
print("=" * 50)

# Load environment
load_dotenv()

# Check Python version
print(f"\n✓ Python version: {sys.version.split()[0]}")
if sys.version_info < (3, 11):
    print("  ⚠️  Warning: Python 3.11+ recommended")

# Check dependencies
dependencies = [
    'django',
    'openai',    # Changed from 'anthropic'
    'mcp',
    'requests',
    'dotenv'     # Note: imports as 'python-dotenv' but check looks for module
]

print("\n📦 Checking dependencies:")
for dep in dependencies:
    try:
        # Special case for python-dotenv which is imported as 'dotenv'
        if dep == 'dotenv':
            import dotenv
            print(f"  ✓ {dep}")
        else:
            __import__(dep)
            print(f"  ✓ {dep}")
    except ImportError:
        print(f"  ✗ {dep} - MISSING!")
        print(f"    Run: pip install {dep}")

# Check API keys
print("\n🔑 Checking API keys:")

# Check for either standard OpenAI Key OR GitHub Token
openai_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

if openai_key:
    print(f"  ✓ OPENAI_API_KEY found: {openai_key[:15]}...")
elif github_token:
    print(f"  ✓ GITHUB_TOKEN found: {github_token[:15]}...")
else:
    print("  ✗ LLM API KEY not configured")
    print("    Edit .env file and add either OPENAI_API_KEY or GITHUB_TOKEN")

# Check VirusTotal Key
vt_key = os.getenv("VIRUSTOTAL_API_KEY")
if vt_key and vt_key != "your_virustotal_api_key_here":
    print(f"  ✓ VIRUSTOTAL_API_KEY: {vt_key[:15]}...")
else:
    print("  ✗ VIRUSTOTAL_API_KEY not configured")
    print("    Edit .env file and add your key")

# Test MCP server import
print("\n🛠️  Testing MCP server:")
try:
    from mcp.server.fastmcp import FastMCP
    print("  ✓ MCP server imports work")
except ImportError as e:
    print(f"  ✗ MCP import failed: {e}")

# Test MCP client import
print("\n🤖 Testing MCP client:")
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    print("  ✓ MCP client imports work")
except ImportError as e:
    print(f"  ✗ MCP client import failed: {e}")

print("\n" + "=" * 50)
print("\n📊 Summary:")
if (openai_key or github_token) and vt_key:
    print("  ✅ Setup looks good! Run: python manage.py runserver")
else:
    print("  ⚠️  Please configure API keys in .env file")

print("\n🚀 Quick Start:")
print("  1. Edit .env with your API keys")
print("  2. Run: python manage.py runserver")
print("  3. Open: http://localhost:8000")
print()