"""
API Views for Surveillance Reports
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from .models import SurveillanceReport
from .serializers import (
    SurveillanceReportSerializer,
    SurveillanceReportCreateSerializer,
    SurveillanceReportListSerializer
)
from .tasks import process_surveillance_report
from rest_framework.permissions import AllowAny  # ← Add this import at top


class SurveillanceReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing surveillance reports
    
    Endpoints:
    - GET /api/reports/ - List all reports
    - POST /api/reports/ - Upload new PDF report
    - GET /api/reports/{id}/ - Get report details
    - GET /api/reports/{id}/download_docx/ - Download generated Word document
    - DELETE /api/reports/{id}/ - Delete report
    """
    
    queryset = SurveillanceReport.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]  # ← Add this line!

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return SurveillanceReportCreateSerializer
        elif self.action == 'list':
            return SurveillanceReportListSerializer
        return SurveillanceReportSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return SurveillanceReport.objects.filter(created_by=user)
        else:
            # No authentication - return all reports
            return SurveillanceReport.objects.all()
        
    def perform_create(self, serializer):
        # Don't set created_by since no authentication
        serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Upload PDF and trigger async processing
        
        Request:
            - title: Report title
            - original_pdf: PDF file
        
        Response:
            - Report object with status 'pending'
            - Processing will happen in background
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Trigger async processing
        process_surveillance_report.delay(serializer.instance.id)
        
        # Return created report using serializer.instance
        return Response(
            {
                'message': 'Report uploaded successfully. Processing started.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Get detailed report information"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """List all reports with pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Optional filtering
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='download-docx')
    def download_docx(self, request, pk=None):
        """
        Download generated Word document
        
        GET /api/reports/{id}/download-docx/
        """
        report = self.get_object()
        
        if not report.generated_docx:
            return Response(
                {'error': 'Word document not yet generated. Report status: ' + report.status},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return file for download
        response = FileResponse(
            report.generated_docx.open('rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{report.title}.docx"'
        
        return response
    
    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, pk=None):
        """
        Download original PDF document
        
        GET /api/reports/{id}/download-pdf/
        """
        report = self.get_object()
        
        if not report.original_pdf:
            return Response(
                {'error': 'PDF file not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return file for download
        response = FileResponse(
            report.original_pdf.open('rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{report.title}.pdf"'
        
        return response
    
    @action(detail=True, methods=['post'], url_path='reprocess')
    def reprocess(self, request, pk=None):
        """
        Reprocess a failed report
        
        POST /api/reports/{id}/reprocess/
        """
        report = self.get_object()
        
        if report.status == 'processing':
            return Response(
                {'error': 'Report is already being processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset status and trigger processing
        report.status = 'pending'
        report.error_message = None
        report.save()
        
        process_surveillance_report.delay(report.id)
        
        return Response(
            {'message': 'Report reprocessing started'},
            status=status.HTTP_200_OK
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete report and associated files"""
        instance = self.get_object()
        
        # Delete files
        if instance.original_pdf:
            instance.original_pdf.delete(save=False)
        if instance.generated_docx:
            instance.generated_docx.delete(save=False)
        
        # Delete record
        self.perform_destroy(instance)
        
        return Response(
            {'message': 'Report deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
