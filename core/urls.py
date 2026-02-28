"""
URL configuration for core app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/analyze/', views.analyze_risk, name='analyze_risk'),
]
