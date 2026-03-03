import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from core.services.llm_agent import run_analysis
from core.models import ChatSession, ChatMessage

def index(request, session_id=None):
    """Render the main chat interface and load history"""
    # Fetch all previous chat tabs from the database
    sessions = ChatSession.objects.all().order_by('-created_at')
    
    chat_messages = []
    current_session_id = None

    # If the user clicked an old chat tab, load its messages
    if session_id:
        try:
            session = ChatSession.objects.get(id=session_id)
            chat_messages = session.messages.all().order_by('created_at')
            current_session_id = str(session.id)
        except ChatSession.DoesNotExist:
            pass

    return render(request, 'index.html', {
        'sessions': sessions,
        'chat_messages': chat_messages,
        'current_session_id': current_session_id
    })

def knowledge_hub(request):
    """Render the educational Knowledge Hub page"""
    return render(request, 'knowledge_hub.html')

def quizzes(request):
    """Render the gamified Quizzes page"""
    return render(request, 'quizzes.html')

def about(request):
    """Render the About Us page"""
    return render(request, 'about.html')

@csrf_exempt
@require_http_methods(["POST"])
async def analyze_risk(request):
    try:
        data = json.loads(request.body)
        user_input = data.get('input', '').strip()
        image_data = data.get('image') 
        session_id = data.get('session_id') # NEW: The frontend will tell us which tab we are in
        
        if not user_input and not image_data:
            return JsonResponse({'error': 'No input or image provided'}, status=400)

        # 1. GET OR CREATE THE CHAT SESSION (Tab)
        if session_id:
            # Get existing session asynchronously
            session = await ChatSession.objects.aget(id=session_id)
        else:
            # Create a new session if this is the first message
            session = await ChatSession.objects.acreate(
                title=user_input[:30] + "..." if user_input else "Image Analysis"
            )

        # 2. LOAD HISTORY FROM DATABASE
        # Fetch all previous messages for this session
        db_messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        history = [
            {"role": msg.role, "content": msg.content} 
            async for msg in db_messages
        ]

        # 3. SAVE THE USER'S NEW MESSAGE
        await ChatMessage.objects.acreate(
            session=session,
            role="user",
            content=user_input if user_input else "[Image Uploaded]"
        )

        # 4. RUN THE AI AGENT (Pass the DB history!)
        result = await run_analysis(user_input=user_input, history=history, image_b64=image_data)
        
        # 5. SAVE THE AI'S RESPONSE
        await ChatMessage.objects.acreate(
            session=session,
            role="assistant",
            content=result
        )
        
        # Return the AI response AND the session ID so the frontend remembers which tab it's in
        return JsonResponse({
            'analysis': result,
            'session_id': str(session.id) 
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Chat session not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST", "DELETE"])    
def delete_session(request, session_id):
    """Deletes a chat session and all its messages from the database"""
    try:
        session = ChatSession.objects.get(id=session_id)
        session.delete()
        return JsonResponse({'success': True})
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)            