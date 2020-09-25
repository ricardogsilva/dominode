import datetime as dt
import typing

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _


class DominodeResource(models.Model):
    DATASET = 'dataset'
    DATASET_COLLECTION = 'dataset_collection'
    QGIS_STYLE = 'qgis_style'
    SLD_STYLE = 'sld_style'
    METADATA_RECORD = 'metadata_record'
    RESOURCE_TYPE_CHOICES = [
        (DATASET, _('Dataset')),
        (DATASET_COLLECTION, _('Dataset collection')),
        (QGIS_STYLE, _('QGIS style')),
        (SLD_STYLE, _('SLD style')),
        (METADATA_RECORD, _('Metadata')),
    ]

    name = models.CharField(
        max_length=255,
        unique=True
    )
    resource_type = models.CharField(
        max_length=30,
        choices=RESOURCE_TYPE_CHOICES,
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
    report = JSONField(encoder=DjangoJSONEncoder, default=dict)

    def __str__(self):
        return (
            f'{self.id} - {self.resource.name} - {self.created} - '
            f'{self.result}'
        )
