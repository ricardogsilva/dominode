from django.urls import (
    include,
    path,
)

from . import views

urlpatterns = [
    path(
        '/',
        views.pygeoapi_root,
        name='pygeoapi-root'
    ),
    path(
        'stac/',
        views.stac_catalog_root,
        name='pygeoapi-stac-catalog-root'
    ),
    path(
        'stac/<str:path>',
        views.stac_catalog_path,
        name='pygeoapi-stac-catalog-path'
    ),
    path(
        'stac/search/',
        views.stac_catalog_path,
        name='pygeoapi-stac-search'
    ),
]