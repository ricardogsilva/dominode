from rest_framework import viewsets

from .. import models
from . import serializers


class DominodeResourceViewSet(viewsets.ModelViewSet):
    queryset = models.DominodeResource.objects.all()
    serializer_class = serializers.DominodeResourceSerializer
    filterset_fields = [
        'name',
        'resource_type',
    ]


class ValidationReportViewSet(viewsets.ModelViewSet):
    queryset = models.ValidationReport.objects.all()
    serializer_class = serializers.ValidationReportSerializer
