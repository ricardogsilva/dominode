from rest_framework import (
    mixins,
    viewsets,
)

from .. import models
from . import serializers


class DominodeResourceViewSet(viewsets.ModelViewSet):
    queryset = models.DominodeResource.objects.all()
    serializer_class = serializers.DominodeResourceSerializer
    filterset_fields = [
        'name',
        'resource_type',
        'artifact_type',
    ]


class ValidationReportViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = models.ValidationReport.objects.all()
    serializer_class = serializers.ValidationReportSerializer
    filterset_fields = [
        'resource__name',
    ]

    def perform_create(self, serializer):
        return serializer.save(validator=self.request.user)
