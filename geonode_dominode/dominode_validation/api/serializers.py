from django.contrib.auth import get_user_model

from rest_framework import serializers

from .. import models


class ValidationReportSerializer(serializers.HyperlinkedModelSerializer):
    validator = serializers.SlugRelatedField(
        'username',
        queryset=get_user_model().objects.all()
    )
    resource = serializers.SlugRelatedField(
        'name',
        queryset=models.DominodeResource.objects.all()
    )

    class Meta:
        model = models.ValidationReport
        fields = [
            'url',
            'resource',
            'result',
            'created',
            'report',
            'validator',
        ]


class DominodeResourceSerializer(serializers.HyperlinkedModelSerializer):
    validation_reports = ValidationReportSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = models.DominodeResource
        fields = [
            'url',
            'name',
            'is_valid',
            'last_validated',
            'resource_type',
            'validation_reports',
        ]

    def validate_name(self, value: str):
        parts = value.split('_')
        if len(parts) not in (3, 4):
            raise serializers.ValidationError('Invalid name')
        version_parts = parts[-1]
        if len(version_parts.split('.')) != 3:
            raise serializers.ValidationError('Invalid name')
        return value
