from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    tokens = models.IntegerField(default=0)  # Starting tokens for new users
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.username

class EmailConfirmationToken(models.Model):
    TOKEN_TYPES = [
        ('registration', 'Registration'),
        ('email_change', 'Email Change'),
        ('password_reset', 'Password Reset'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES, default='registration')
    new_email = models.EmailField(blank=True, null=True)  # For email changes
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    def is_expired(self):
        # Token expires after 24 hours
        return timezone.now() > self.created_at + timedelta(hours=24)
    
    def __str__(self):
        return f"Email confirmation for {self.user.username} ({self.token_type})"

class Arena(models.Model):
    TIER_CHOICES = [
        ('recruit', 'Recruit'),
        ('veteran', 'Veteran'),
        ('champion', 'Champion'),
        ('elite', 'Elite'),
    ]
    
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    token_cost = models.IntegerField()  # Tokens required to join
    description = models.TextField()
    max_participants = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.tier})"
    
    class Meta:
        ordering = ['token_cost']

class Contestant(models.Model):
    SUBMISSION_TYPES = [
        ('video', 'Video'),
        ('image', 'Image'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contestants')
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name='contestants')
    submission_type = models.CharField(max_length=10, choices=SUBMISSION_TYPES, default='video')
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='contestant_videos/', blank=True, null=True)
    image_file = models.ImageField(upload_to='contestant_images/', blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.arena.name}"
    
    class Meta:
        ordering = ['-votes', '-created_at']
        unique_together = ['user', 'arena']  # One submission per user per arena

class Vote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='votes')
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE, related_name='vote_records')
    is_free_vote = models.BooleanField(default=True)  # Free votes don't cost tokens
    tokens_spent = models.IntegerField(default=0)  # Tokens spent if not free
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'contestant']  # One vote per user per contestant
    
    def __str__(self):
        return f"{self.user.username} voted for {self.contestant.user.username}"

class TokenTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('vote', 'Vote'),
        ('arena_entry', 'Arena Entry'),
        ('refund', 'Refund'),
        ('bonus', 'Bonus'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='token_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()  # Positive for additions, negative for deductions
    description = models.TextField(blank=True)
    related_contestant = models.ForeignKey(Contestant, on_delete=models.SET_NULL, null=True, blank=True)
    related_arena = models.ForeignKey(Arena, on_delete=models.SET_NULL, null=True, blank=True)
    related_payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} tokens"
    
    class Meta:
        ordering = ['-created_at']

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments')
    stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount in dollars
    tokens = models.IntegerField()  # Number of tokens purchased
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} - {self.tokens} tokens - {self.status}"
    
    class Meta:
        ordering = ['-created_at']