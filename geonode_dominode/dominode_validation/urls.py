from django.urls import (
    include,
    path,
)

from . import views
from .api.urls import router

urlpatterns = [
    path('api/', include(router.urls)),
    path(
        'resources/',
        views.DominodeResourceListView.as_view(),
        name='dominode-resource-list'
    ),
    path(
        'resources/<int:pk>',
        views.DominodeResourceDetailView.as_view(),
        name='dominode-resource-detail'
    ),
    path(
        'resources/<int:resource>/validation-reports/',
        views.ValidationReportListView.as_view(),
        name='validation-report-list'
    ),
    path(
        'resources/validation-reports/<int:pk>',
        views.ValidationReportDetailView.as_view(),
        name='validation-report-detail'
    ),
]