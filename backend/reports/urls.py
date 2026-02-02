"""
URL Configuration for Reports API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurveillanceReportViewSet

router = DefaultRouter()
router.register(r'reports', SurveillanceReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
