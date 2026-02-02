"""
DRF Serializers for Surveillance Reports
"""
from rest_framework import serializers
from .models import SurveillanceReport


class SurveillanceReportSerializer(serializers.ModelSerializer):
    """Serializer for surveillance report model"""

    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    original_file_url = serializers.SerializerMethodField()
    original_pdf_url = serializers.SerializerMethodField()
    generated_docx_url = serializers.SerializerMethodField()

    class Meta:
        model = SurveillanceReport
        fields = [
            'id', 'title', 'status', 'error_message',
            'original_file', 'original_file_url', 'file_type',
            'original_pdf', 'original_pdf_url',
            'generated_docx', 'generated_docx_url',
            'period_start', 'period_end',
            'total_mentions', 'mentions_change_percent',
            'total_reach', 'reach_change_percent',
            'presence_passive_data', 'presence_active_data',
            'sentiment_data', 'emotion_data',
            'sources_data', 'languages_data',
            'topics_data', 'hashtags_data', 'influencers_data',
            'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'error_message', 'generated_docx', 'file_type',
            'period_start', 'period_end',
            'total_mentions', 'mentions_change_percent',
            'total_reach', 'reach_change_percent',
            'presence_passive_data', 'presence_active_data',
            'sentiment_data', 'emotion_data',
            'sources_data', 'languages_data',
            'topics_data', 'hashtags_data', 'influencers_data',
            'created_at', 'updated_at'
        ]

    def get_original_file_url(self, obj):
        """Get full URL for original file (PDF or PPTX)"""
        if obj.original_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.original_file.url)
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

    class Meta:
        model = SurveillanceReport
        fields = [
            'id', 'title', 'status', 'file_type',
            'period_start', 'period_end',
            'total_mentions', 'total_reach',
            'presence_passive_data', 'presence_active_data',
            'sentiment_data',
            'created_by_username', 'created_at'
        ]
