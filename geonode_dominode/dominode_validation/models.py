import datetime as dt
import typing

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _


class DominodeResource(models.Model):
    DATASET = 'dataset'
    METADATA_RECORD = 'metadata_record'
    STYLE = 'style'
    OTHER_ARTIFACT_TYPE = 'other_artifact_type'

    ARTIFACT_TYPE_CHOICES = [
        (DATASET, _('Dataset')),
        (METADATA_RECORD, _('Metadata')),
        (STYLE, _('Style')),
        (OTHER_ARTIFACT_TYPE, _('Other')),
    ]

    DOCUMENT = 'document'
    RASTER = 'raster'
    VECTOR = 'vector'
    COLLECTION = 'collection'
    OTHER_RESOURCE_TYPE = 'other_resource_type'

    RESOURCE_TYPE_CHOICES = [
        (DOCUMENT, _('Document')),
        (RASTER, _('Raster')),
        (VECTOR, _('Vector')),
        (COLLECTION, _('Collection')),
        (OTHER_RESOURCE_TYPE, _('Other')),
    ]

    name = models.CharField(
        max_length=255,
        unique=True
    )
    resource_type = models.CharField(
        max_length=30,
        choices=RESOURCE_TYPE_CHOICES,
        default=VECTOR
    )
    artifact_type = models.CharField(
        max_length=30,
        choices=ARTIFACT_TYPE_CHOICES,
        default=DATASET
    )

    def __str__(self):
        return f'{self.id} - {self.name}'

    def is_valid(self) -> bool:
        latest_report = self._get_latest_report()
        return latest_report.result if latest_report is not None else False

    def last_validated(self) -> typing.Union[dt.datetime, str]:
        latest_report = self._get_latest_report()
        return latest_report.created if latest_report is not None else None

    def _get_latest_report(self):
        return self.validation_reports.order_by('-created').first()


class ValidationReport(models.Model):
    resource = models.ForeignKey(
        DominodeResource,
        on_delete=models.CASCADE,
        related_name='validation_reports'
    )
    result = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    validator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    validation_datetime = models.DateTimeField()
    checklist_name = models.CharField(max_length=255)
    checklist_description = models.TextField()
    checklist_steps = JSONField(encoder=DjangoJSONEncoder, default=list)

    def __str__(self):
        return (
            f'{self.id} - {self.resource.name} - {self.created} - '
            f'{self.result}'
        )
