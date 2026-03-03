#!/usr/bin/env python
"""
CyberGuard Verification: Handles 'Missing' dependencies due to .gitignore
"""
import os
import sys
import asyncio
import django
from dotenv import load_dotenv

async def main():
    print("🔍 CyberGuard Environment Verification")
    print("=" * 60)

    # 1. Load Environment (Fails if .env was ignored)
    env_exists = load_dotenv()
    if not env_exists:
        print("⚠️  Warning: .env file not found. Create one from .env.example")

    # 2. Dependency Check (Includes the new 'dns' library)
    # Your original script checked for django, openai, mcp, and requests
    dependencies = ['django', 'openai', 'mcp', 'requests', 'dotenv', 'dns']
    print("\n📦 Checking dependencies:")
    for dep in dependencies:
        try:
            # Note: dnspython is imported as 'dns.resolver'
            if dep == 'dns':
                import dns.resolver
            elif dep == 'dotenv':
                import dotenv
            else:
                __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} - MISSING! Run: pip install -r requirements.txt")

    # 3. Database Check (Validates if migrations were skipped)
    print("\n🗄️  Database & Django Check:")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyberguard_project.settings')
        django.setup()
        from core.models import ChatSession
        # Django 5.x async database check
        count = await ChatSession.objects.acount()
        print(f"  ✓ Database: Ready. {count} sessions found.")
    except Exception as e:
        print(f"  ✗ Database Error: {e}")
        print("    💡 Tip: Since db.sqlite3 is ignored, run: python manage.py migrate")

    print("\n" + "=" * 60)
    print("🚀 Quick Recovery:")
    print("   1. pip install -r requirements.txt")
    print("   2. python manage.py migrate")

if __name__ == "__main__":
    asyncio.run(main())