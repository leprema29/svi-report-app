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


class ReportGroup(models.Model):
    """Model for grouping multiple source reports into one comprehensive report"""

    GROUP_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    title = models.CharField(max_length=255, help_text="Common title/keyword for all reports in this group")

    # Generated comprehensive report
    generated_docx = models.FileField(upload_to='reports/grouped/%Y/%m/', null=True, blank=True)

    # Period (merged from all source reports)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    # Merged KPI data
    merged_presence_passive = models.JSONField(default=dict, blank=True)
    merged_presence_active = models.JSONField(default=dict, blank=True)
    merged_sentiment = models.JSONField(default=dict, blank=True)
    merged_emotion = models.JSONField(default=dict, blank=True)
    merged_sources = models.JSONField(default=dict, blank=True)
    merged_languages = models.JSONField(default=dict, blank=True)
    merged_topics = models.JSONField(default=list, blank=True)
    merged_hashtags = models.JSONField(default=list, blank=True)
    merged_influencers = models.JSONField(default=list, blank=True)
    merged_reach_breakdown = models.JSONField(default=list, blank=True)
    merged_demographics = models.JSONField(default=dict, blank=True)

    # Manual entry fields for KPIs not available in source reports
    manual_followers = models.IntegerField(null=True, blank=True, help_text="Manual entry for followers count")
    manual_likes = models.IntegerField(null=True, blank=True, help_text="Manual entry for likes count")
    manual_shares = models.IntegerField(null=True, blank=True, help_text="Manual entry for shares count")
    manual_comments = models.IntegerField(null=True, blank=True, help_text="Manual entry for comments count")
    manual_views = models.IntegerField(null=True, blank=True, help_text="Manual entry for views count")

    # Data source references (tracks which data came from which report)
    data_sources = models.JSONField(default=dict, blank=True)
    # Structure: {field_name: [{source_report_id, source_filename, source_type, value}, ...]}

    # Source report types included
    included_report_types = models.JSONField(default=list, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=GROUP_STATUS, default='pending')
    error_message = models.TextField(blank=True, null=True)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Report Group"
        verbose_name_plural = "Report Groups"

    def __str__(self):
        return f"{self.title} - Group ({self.source_reports.count()} reports)"

    def get_source_filenames(self):
        """Get list of source filenames"""
        filenames = []
        for report in self.source_reports.all():
            if report.original_file:
                import os
                filenames.append(os.path.basename(report.original_file.name))
            elif report.original_pdf:
                import os
                filenames.append(os.path.basename(report.original_pdf.name))
        return filenames


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

    REPORT_TYPE_CHOICES = [
        ('mention_dashboard', 'Mention.com Dashboard'),
        ('brand24_analysis', 'Brand24 Analysis'),
        ('brand24_demographics', 'Brand24 Demographics'),
        ('unknown', 'Unknown'),
    ]

    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES, default='unknown')
    report_type_display = models.CharField(max_length=100, blank=True)

    # Link to report group (for multi-report processing)
    report_group = models.ForeignKey(
        ReportGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_reports'
    )

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
    reach_breakdown_data = models.JSONField(default=list, blank=True)

    # Demographics data (for Brand24 Demographics reports)
    demographics_data = models.JSONField(default=dict, blank=True)
    # Structure: {gender, age, countries, occupation, education, interests}

    # Available/Unavailable KPIs for this report type
    available_kpis = models.JSONField(default=list, blank=True)
    unavailable_kpis = models.JSONField(default=list, blank=True)

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
