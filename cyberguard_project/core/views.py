"""
Views for CyberGuard
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from core.services.llm_agent import run_analysis
import asyncio


def index(request):
    """
    Render the main page
    """
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
async def analyze_risk(request):
    """
    Async view to analyze user input for security threats
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        user_input = data.get('input', '').strip()
        
        if not user_input:
            return JsonResponse({
                'error': 'No input provided'
            }, status=400)
        
        # Run analysis using MCP-powered agent
        result = await run_analysis(user_input)
        
        return JsonResponse({
            'analysis': result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Server error: {str(e)}'
        }, status=500)
