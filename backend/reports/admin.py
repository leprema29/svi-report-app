"""
Admin configuration for reports
"""
from django.contrib import admin
from .models import SurveillanceReport


@admin.register(SurveillanceReport)
class SurveillanceReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'created_by', 'total_mentions', 'total_reach', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'status', 'created_by')
        }),
        ('Files', {
            'fields': ('original_pdf', 'generated_docx')
        }),
        ('Extracted KPIs', {
            'fields': (
                'period_start', 'period_end',
                'total_mentions', 'mentions_change_percent',
                'total_reach', 'reach_change_percent'
            )
        }),
        ('JSON Data', {
            'fields': (
                'sentiment_data', 'emotion_data',
                'sources_data', 'languages_data',
                'topics_data', 'hashtags_data', 'influencers_data'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('error_message', 'created_at', 'updated_at')
        }),
    )