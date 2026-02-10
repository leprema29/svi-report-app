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
import os

from .models import SurveillanceReport, ReportGroup
from .serializers import (
    SurveillanceReportSerializer,
    SurveillanceReportCreateSerializer,
    SurveillanceReportListSerializer,
    ReportGroupSerializer,
    ReportGroupCreateSerializer,
    ReportGroupListSerializer
)
from .tasks import process_surveillance_report, process_report_group
from rest_framework.permissions import AllowAny


class SurveillanceReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing surveillance reports

    Endpoints:
    - GET /api/reports/ - List all reports
    - POST /api/reports/ - Upload new PDF/PPTX report
    - GET /api/reports/{id}/ - Get report details
    - GET /api/reports/{id}/download_docx/ - Download generated Word document
    - GET /api/reports/{id}/download_original/ - Download original file (PDF or PPTX)
    - DELETE /api/reports/{id}/ - Delete report
    """

    queryset = SurveillanceReport.objects.all()
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

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
        Upload PDF or PPTX and trigger async processing

        Request:
            - title: Report title
            - original_file: PDF or PPTX file (preferred)
            - original_pdf: PDF file (legacy, for backwards compatibility)

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

        # Filter by file type
        file_type_filter = request.query_params.get('file_type', None)
        if file_type_filter:
            queryset = queryset.filter(file_type=file_type_filter)

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
        Download original PDF document (legacy endpoint)

        GET /api/reports/{id}/download-pdf/
        """
        report = self.get_object()

        # Check for both new and legacy file fields
        original_file = report.get_original_file()

        if not original_file:
            return Response(
                {'error': 'Original file not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Determine content type based on file extension
        ext = os.path.splitext(original_file.name)[1].lower()
        if ext == '.pptx':
            content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        else:
            content_type = 'application/pdf'

        # Return file for download
        response = FileResponse(
            original_file.open('rb'),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{report.title}{ext}"'

        return response

    @action(detail=True, methods=['get'], url_path='download-original')
    def download_original(self, request, pk=None):
        """
        Download original file (PDF or PPTX)

        GET /api/reports/{id}/download-original/
        """
        report = self.get_object()

        # Get the original file
        original_file = report.get_original_file()

        if not original_file:
            return Response(
                {'error': 'Original file not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Determine content type based on file extension
        ext = os.path.splitext(original_file.name)[1].lower()
        if ext == '.pptx':
            content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        else:
            content_type = 'application/pdf'

        # Return file for download
        response = FileResponse(
            original_file.open('rb'),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{report.title}{ext}"'

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
        if instance.original_file:
            instance.original_file.delete(save=False)
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


class ReportGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing report groups (multi-report processing)

    Endpoints:
    - GET /api/report-groups/ - List all report groups
    - POST /api/report-groups/ - Upload multiple reports for merged processing
    - GET /api/report-groups/{id}/ - Get report group details
    - GET /api/report-groups/{id}/download_docx/ - Download generated merged Word document
    - DELETE /api/report-groups/{id}/ - Delete report group
    """

    queryset = ReportGroup.objects.all()
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ReportGroupCreateSerializer
        elif self.action == 'list':
            return ReportGroupListSerializer
        return ReportGroupSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return ReportGroup.objects.filter(created_by=user)
        else:
            return ReportGroup.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Upload multiple PDF/PPTX files and create a report group

        Request:
            - title: Common title/keyword for all reports
            - files: List of PDF or PPTX files
            - manual_followers: (optional) Manual entry for followers
            - manual_likes: (optional) Manual entry for likes
            - manual_shares: (optional) Manual entry for shares
            - manual_comments: (optional) Manual entry for comments
            - manual_views: (optional) Manual entry for views

        Response:
            - Report group object with status 'pending'
            - Processing will happen in background
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the report group
        report_group = ReportGroup.objects.create(
            title=serializer.validated_data['title'],
            manual_followers=serializer.validated_data.get('manual_followers'),
            manual_likes=serializer.validated_data.get('manual_likes'),
            manual_shares=serializer.validated_data.get('manual_shares'),
            manual_comments=serializer.validated_data.get('manual_comments'),
            manual_views=serializer.validated_data.get('manual_views'),
        )

        # Create individual reports for each file
        files = serializer.validated_data['files']
        created_report_ids = []

        for f in files:
            ext = os.path.splitext(f.name)[1].lower()

            # Create individual report
            report = SurveillanceReport.objects.create(
                title=serializer.validated_data['title'],
                original_file=f,
                report_group=report_group,
                status='pending'
            )
            created_report_ids.append(report.id)

        # Trigger async processing of the report group
        process_report_group.delay(report_group.id)

        # Return response
        response_serializer = ReportGroupSerializer(report_group, context={'request': request})
        return Response(
            {
                'message': f'Report group created with {len(files)} files. Processing started.',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def list(self, request, *args, **kwargs):
        """List all report groups with pagination"""
        queryset = self.filter_queryset(self.get_queryset())

        # Optional filtering by status
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
        Download generated merged Word document

        GET /api/report-groups/{id}/download-docx/
        """
        report_group = self.get_object()

        if not report_group.generated_docx:
            return Response(
                {'error': 'Word document not yet generated. Status: ' + report_group.status},
                status=status.HTTP_404_NOT_FOUND
            )

        response = FileResponse(
            report_group.generated_docx.open('rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{report_group.title}_merged.docx"'
        return response

    @action(detail=True, methods=['post'], url_path='reprocess')
    def reprocess(self, request, pk=None):
        """
        Reprocess a failed report group

        POST /api/report-groups/{id}/reprocess/
        """
        report_group = self.get_object()

        if report_group.status == 'processing':
            return Response(
                {'error': 'Report group is already being processed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset status and trigger processing
        report_group.status = 'pending'
        report_group.error_message = None
        report_group.save()

        process_report_group.delay(report_group.id)

        return Response(
            {'message': 'Report group reprocessing started'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'], url_path='update-manual')
    def update_manual(self, request, pk=None):
        """
        Update manual entry fields and regenerate the report

        PATCH /api/report-groups/{id}/update-manual/
        """
        report_group = self.get_object()

        # Update manual fields
        manual_fields = ['manual_followers', 'manual_likes', 'manual_shares',
                        'manual_comments', 'manual_views']

        updated = False
        for field in manual_fields:
            if field in request.data:
                setattr(report_group, field, request.data.get(field))
                updated = True

        if updated:
            report_group.save()
            # Trigger reprocessing to regenerate the report
            report_group.status = 'pending'
            report_group.save()
            process_report_group.delay(report_group.id)

            return Response(
                {'message': 'Manual values updated. Regenerating report.'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'message': 'No fields to update'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete report group and all associated reports/files"""
        instance = self.get_object()

        # Delete source reports
        for report in instance.source_reports.all():
            if report.original_file:
                report.original_file.delete(save=False)
            if report.original_pdf:
                report.original_pdf.delete(save=False)
            if report.generated_docx:
                report.generated_docx.delete(save=False)
            report.delete()

        # Delete group's generated file
        if instance.generated_docx:
            instance.generated_docx.delete(save=False)

        # Delete record
        self.perform_destroy(instance)

        return Response(
            {'message': 'Report group deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
