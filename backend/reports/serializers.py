"""
DRF Serializers for Surveillance Reports
"""
from rest_framework import serializers
from .models import SurveillanceReport, ReportGroup
import os


class SurveillanceReportSerializer(serializers.ModelSerializer):
    """Serializer for surveillance report model"""

    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    original_file_url = serializers.SerializerMethodField()
    original_file_name = serializers.SerializerMethodField()
    original_pdf_url = serializers.SerializerMethodField()
    generated_docx_url = serializers.SerializerMethodField()

    class Meta:
        model = SurveillanceReport
        fields = [
            'id', 'title', 'status', 'error_message',
            'original_file', 'original_file_url', 'original_file_name', 'file_type',
            'report_type', 'report_type_display',
            'available_kpis', 'unavailable_kpis',
            'original_pdf', 'original_pdf_url',
            'generated_docx', 'generated_docx_url',
            'period_start', 'period_end',
            'total_mentions', 'mentions_change_percent',
            'total_reach', 'reach_change_percent',
            'presence_passive_data', 'presence_active_data',
            'sentiment_data', 'emotion_data',
            'sources_data', 'languages_data',
            'topics_data', 'hashtags_data', 'influencers_data',
            'reach_breakdown_data', 'demographics_data',
            'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'error_message', 'generated_docx', 'file_type',
            'report_type', 'report_type_display',
            'available_kpis', 'unavailable_kpis',
            'period_start', 'period_end',
            'total_mentions', 'mentions_change_percent',
            'total_reach', 'reach_change_percent',
            'presence_passive_data', 'presence_active_data',
            'sentiment_data', 'emotion_data',
            'sources_data', 'languages_data',
            'topics_data', 'hashtags_data', 'influencers_data',
            'reach_breakdown_data', 'demographics_data',
            'created_at', 'updated_at'
        ]

    def get_original_file_url(self, obj):
        """Get full URL for original file (PDF or PPTX)"""
        if obj.original_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.original_file.url)
        return None

    def get_original_file_name(self, obj):
        """Get original filename"""
        if obj.original_file:
            return os.path.basename(obj.original_file.name)
        elif obj.original_pdf:
            return os.path.basename(obj.original_pdf.name)
        return None

    def get_original_pdf_url(self, obj):
        """Get full URL for original PDF (legacy)"""
        if obj.original_pdf:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.original_pdf.url)
        return None

    def get_generated_docx_url(self, obj):
        """Get full URL for generated Word document"""
        if obj.generated_docx:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.generated_docx.url)
        return None


class SurveillanceReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating surveillance reports"""

    # Accept either original_file or original_pdf
    original_file = serializers.FileField(required=False, allow_null=True)
    original_pdf = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = SurveillanceReport
        fields = ['id', 'title', 'original_file', 'original_pdf', 'status', 'created_at', 'updated_at', 'generated_docx']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'generated_docx']

    def validate(self, data):
        """Ensure at least one file is provided"""
        if not data.get('original_file') and not data.get('original_pdf'):
            raise serializers.ValidationError("Either original_file or original_pdf must be provided")
        return data


class SurveillanceReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""

    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    original_file_name = serializers.SerializerMethodField()

    class Meta:
        model = SurveillanceReport
        fields = [
            'id', 'title', 'status', 'file_type',
            'original_file_name',
            'report_type', 'report_type_display',
            'available_kpis', 'unavailable_kpis',
            'period_start', 'period_end',
            'total_mentions', 'total_reach',
            'presence_passive_data', 'presence_active_data',
            'sentiment_data', 'demographics_data',
            'created_by_username', 'created_at'
        ]

    def get_original_file_name(self, obj):
        """Get original filename"""
        if obj.original_file:
            return os.path.basename(obj.original_file.name)
        elif obj.original_pdf:
            return os.path.basename(obj.original_pdf.name)
        return None


class ReportGroupSerializer(serializers.ModelSerializer):
    """Serializer for report group model"""

    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    generated_docx_url = serializers.SerializerMethodField()
    source_reports = SurveillanceReportListSerializer(many=True, read_only=True)
    source_filenames = serializers.SerializerMethodField()

    class Meta:
        model = ReportGroup
        fields = [
            'id', 'title', 'status', 'error_message',
            'generated_docx', 'generated_docx_url',
            'period_start', 'period_end',
            'merged_presence_passive', 'merged_presence_active',
            'merged_sentiment', 'merged_emotion',
            'merged_sources', 'merged_languages',
            'merged_topics', 'merged_hashtags',
            'merged_influencers', 'merged_reach_breakdown',
            'merged_demographics',
            'manual_followers', 'manual_likes', 'manual_shares',
            'manual_comments', 'manual_views',
            'data_sources', 'included_report_types',
            'source_reports', 'source_filenames',
            'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'error_message', 'generated_docx',
            'merged_presence_passive', 'merged_presence_active',
            'merged_sentiment', 'merged_emotion',
            'merged_sources', 'merged_languages',
            'merged_topics', 'merged_hashtags',
            'merged_influencers', 'merged_reach_breakdown',
            'merged_demographics', 'data_sources',
            'included_report_types', 'source_reports',
            'period_start', 'period_end',
            'created_at', 'updated_at'
        ]

    def get_generated_docx_url(self, obj):
        """Get full URL for generated Word document"""
        if obj.generated_docx:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.generated_docx.url)
        return None

    def get_source_filenames(self, obj):
        """Get list of source filenames"""
        return obj.get_source_filenames()


class ReportGroupCreateSerializer(serializers.Serializer):
    """Serializer for creating report groups with multiple file uploads"""

    title = serializers.CharField(max_length=255, help_text="Common title/keyword for all reports")
    files = serializers.ListField(
        child=serializers.FileField(),
        min_length=1,
        max_length=10,
        help_text="List of PDF or PPTX files to process"
    )
    manual_followers = serializers.IntegerField(required=False, allow_null=True)
    manual_likes = serializers.IntegerField(required=False, allow_null=True)
    manual_shares = serializers.IntegerField(required=False, allow_null=True)
    manual_comments = serializers.IntegerField(required=False, allow_null=True)
    manual_views = serializers.IntegerField(required=False, allow_null=True)

    def validate_files(self, files):
        """Validate that all files are PDF or PPTX"""
        allowed_extensions = ['.pdf', '.pptx']
        for f in files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(
                    f"File '{f.name}' has unsupported format. Only PDF and PPTX files are allowed."
                )
        return files


class ReportGroupListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for report group list view"""

    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    source_count = serializers.SerializerMethodField()
    source_filenames = serializers.SerializerMethodField()

    class Meta:
        model = ReportGroup
        fields = [
            'id', 'title', 'status',
            'period_start', 'period_end',
            'included_report_types',
            'source_count', 'source_filenames',
            'created_by_username', 'created_at'
        ]

    def get_source_count(self, obj):
        return obj.source_reports.count()

    def get_source_filenames(self, obj):
        return obj.get_source_filenames()
