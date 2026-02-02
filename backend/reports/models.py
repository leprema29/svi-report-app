"""
Surveillance Report Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


def report_upload_path(instance, filename):
    """Generate upload path based on file type"""
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.pdf':
        return f'reports/pdf/%Y/%m/{filename}'
    elif ext == '.pptx':
        return f'reports/pptx/%Y/%m/{filename}'
    return f'reports/other/%Y/%m/{filename}'


class SurveillanceReport(models.Model):
    """Model for storing surveillance report metadata"""

    REPORT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('pptx', 'PPTX'),
    ]

    title = models.CharField(max_length=255)

    # Support both PDF and PPTX
    original_file = models.FileField(
        upload_to='reports/uploads/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'pptx'])],
        null=True,
        blank=True
    )
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='pdf')

    # Legacy field for backwards compatibility
    original_pdf = models.FileField(upload_to='reports/pdf/%Y/%m/', null=True, blank=True)

    generated_docx = models.FileField(upload_to='reports/docx/%Y/%m/', null=True, blank=True)

    # Period
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    # Legacy KPIs (for backwards compatibility)
    total_mentions = models.IntegerField(default=0)
    mentions_change_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_reach = models.BigIntegerField(default=0)
    reach_change_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # New KPI Structure - Presence Passive
    presence_passive_data = models.JSONField(default=dict, blank=True)
    # Structure: {followers, followers_evolution, views, views_evolution, potential_reach, reach_evolution}

    # New KPI Structure - Presence Active
    presence_active_data = models.JSONField(default=dict, blank=True)
    # Structure: {comments, likes, shares}

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

    def get_original_file(self):
        """Get the original file (either new field or legacy PDF field)"""
        if self.original_file:
            return self.original_file
        return self.original_pdf

    def save(self, *args, **kwargs):
        """Override save to set file_type based on file extension"""
        if self.original_file:
            import os
            ext = os.path.splitext(self.original_file.name)[1].lower()
            if ext == '.pdf':
                self.file_type = 'pdf'
            elif ext == '.pptx':
                self.file_type = 'pptx'
        elif self.original_pdf:
            self.file_type = 'pdf'
        super().save(*args, **kwargs)
