from django.contrib import admin
from django.contrib.postgres.fields import JSONField

from django_json_widget.widgets import JSONEditorWidget

from . import models


class ValidationReportInline(admin.StackedInline):
    model = models.ValidationReport
    extra = 0
    readonly_fields = ('created',)
    formfield_overrides = {
        JSONField: {
            'widget': JSONEditorWidget,
        }
    }


@admin.register(models.DominodeResource)
class DominodeResourceAdmin(admin.ModelAdmin):
    inlines = (
        ValidationReportInline,
    )
    list_display = (
        'name',
        'resource_type',
        'artifact_type',
        'is_valid',
        'last_validated',
    )
    list_filter = (
        'resource_type',
        'artifact_type',
    )
    search_fields = (
        'name',
    )
