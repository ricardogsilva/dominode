from django.urls import path

from . import views

urlpatterns = [
    path(
        '',
        views.TopomapListView.as_view(),
        name='topomap-list'
    ),
    path(
        'v<str:version>/series-<int:series>/<str:sheet>/',
        views.SheetDetailView.as_view(),
        name='sheet-detail',
    ),
    path(
        'v<str:version>/series-<int:series>/<str:sheet>/<str:paper_size>/',
        views.TopomapSheetDownloadView.as_view(),
        name='sheet-download',
    ),
]
