from django.db import models
from django.contrib.auth.models import User as AuthUser

# Create your models here.
class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)


class Interview(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='interviews')
    role = models.CharField(max_length=200)
    technology = models.CharField(max_length=500, blank=True, null=True)
    difficulty = models.CharField(max_length=50, default='mid')
    focus = models.CharField(max_length=50, default='balanced')
    persona = models.CharField(max_length=50, default='neutral')
    conversation = models.TextField(help_text="JSON string of conversation history")
    ai_review = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0, help_text="Score out of 100")
    strengths = models.TextField(blank=True, null=True)
    improvements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.created_at.strftime('%Y-%m-%d')}"


