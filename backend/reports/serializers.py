"""
DRF Serializers for Surveillance Reports
"""
from rest_framework import serializers
from .models import SurveillanceReport


class SurveillanceReportSerializer(serializers.ModelSerializer):
    """Serializer for surveillance report model"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    original_pdf_url = serializers.SerializerMethodField()
    generated_docx_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SurveillanceReport
        fields = [
            'id', 'title', 'status', 'error_message',
            'original_pdf', 'original_pdf_url',
            'generated_docx', 'generated_docx_url',
            'period_start', 'period_end',
            'total_mentions', 'mentions_change_percent',
            'total_reach', 'reach_change_percent',
            'sentiment_data', 'emotion_data',
            'sources_data', 'languages_data',
            'topics_data', 'hashtags_data', 'influencers_data',
            'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'error_message', 'generated_docx',
            'period_start', 'period_end',
            'total_mentions', 'mentions_change_percent',
            'total_reach', 'reach_change_percent',
            'sentiment_data', 'emotion_data',
            'sources_data', 'languages_data',
            'topics_data', 'hashtags_data', 'influencers_data',
            'created_at', 'updated_at'
        ]
    
    def get_original_pdf_url(self, obj):
        """Get full URL for original PDF"""
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
    
    class Meta:
        model = SurveillanceReport
        exclude = ['created_by']  # ← Correct!
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'generated_docx']

    
    # def create(self, validated_data):
    #     """Create report and set created_by from request user"""
    #     request = self.context.get('request')
    #     validated_data['created_by'] = request.user
    #     return super().create(validated_data)


class SurveillanceReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = SurveillanceReport
        fields = [
            'id', 'title', 'status',
            'period_start', 'period_end',
            'total_mentions', 'total_reach',
            'created_by_username', 'created_at'
        ]
