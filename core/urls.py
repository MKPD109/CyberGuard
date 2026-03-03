"""
URL configuration for core app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/<uuid:session_id>/', views.index, name='chat_session'), # NEW: For loading old chats
    path('knowledge-hub/', views.knowledge_hub, name='knowledge_hub'),
    path('quizzes/', views.quizzes, name='quizzes'),
    path('about/', views.about, name='about'),
    path('api/analyze/', views.analyze_risk, name='analyze_risk'),
    path('api/delete-session/<uuid:session_id>/', views.delete_session, name='delete_session'),
]