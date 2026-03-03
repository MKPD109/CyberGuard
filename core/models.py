import uuid
from django.db import models

class ChatSession(models.Model):
    """Represents a single chat tab/conversation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"

class ChatMessage(models.Model):
    """Represents an individual message (user or AI) inside a session"""
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=50) # Will be 'user', 'assistant', or 'tool'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Ensures messages always load in chronological order

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."