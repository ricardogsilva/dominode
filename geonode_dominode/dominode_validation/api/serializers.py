from django.contrib.auth import get_user_model

from rest_framework import serializers

from .. import models


class ValidationReportSerializer(serializers.HyperlinkedModelSerializer):
    # validator = serializers.SlugRelatedField(
    #     'username',
    #     queryset=get_user_model().objects.all()
    # )
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
            'validator',
            'validation_datetime',
            'checklist_name',
            'checklist_description',
            'checklist_steps',
        ]
        read_only_fields = [
            'validator',
        ]


class DominodeResourceSerializer(serializers.HyperlinkedModelSerializer):
    num_validation_reports = serializers.SerializerMethodField()

    class Meta:
        model = models.DominodeResource
        fields = [
            'url',
            'name',
            'resource_type',
            'artifact_type',
            'is_valid',
            'last_validated',
            'num_validation_reports',
        ]

    def get_num_validation_reports(self, obj):
        return obj.validation_reports.count()

    def validate_name(self, value: str):
        parts = value.split('_')
        if len(parts) not in (3, 4):
            raise serializers.ValidationError('Invalid name')
        version_parts = parts[-1]
        if len(version_parts.split('.')) != 3:
            raise serializers.ValidationError('Invalid name')
        return value
