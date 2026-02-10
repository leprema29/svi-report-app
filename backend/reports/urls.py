"""
URL Configuration for Reports API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurveillanceReportViewSet, ReportGroupViewSet

router = DefaultRouter()
router.register(r'reports', SurveillanceReportViewSet, basename='report')
router.register(r'report-groups', ReportGroupViewSet, basename='report-group')

urlpatterns = [
    path('', include(router.urls)),
]
