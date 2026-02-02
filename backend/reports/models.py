"""
Surveillance Report Models
"""
from django.db import models
from django.contrib.auth.models import User


class SurveillanceReport(models.Model):
    """Model for storing surveillance report metadata"""
    
    REPORT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    title = models.CharField(max_length=255)
    original_pdf = models.FileField(upload_to='reports/pdf/%Y/%m/')
    generated_docx = models.FileField(upload_to='reports/docx/%Y/%m/', null=True, blank=True)
    
    # Extracted KPIs
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    total_mentions = models.IntegerField(default=0)
    mentions_change_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_reach = models.BigIntegerField(default=0)
    reach_change_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Sentiment data (stored as JSON)
    sentiment_data = models.JSONField(default=dict)
    emotion_data = models.JSONField(default=dict)
    sources_data = models.JSONField(default=dict)
    languages_data = models.JSONField(default=dict)
    topics_data = models.JSONField(default=list)
    hashtags_data = models.JSONField(default=list)
    influencers_data = models.JSONField(default=list)
    
    # Metadata
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}"
