from django.urls import (
    include,
    path,
)

from . import views

urlpatterns = [
    path(
        '',
        views.pygeoapi_root,
        name='pygeoapi-root'
    ),
    path(
        'openapi/',
        views.pygeoapi_openapi_endpoint,
        name='pygeoapi-openapi'
    ),
    path(
        'conformance/',
        views.pygeoapi_conformance_endpoint,
        name='pygeoapi-conformance'
    ),
    path(
        'collections/',
        views.pygeoapi_collections_endpoint,
        name='pygeoapi-collection-list'
    ),
    path(
        'collections/<str:name>/',
        views.pygeoapi_collections_endpoint,
        name='pygeoapi-collection-detail'
    ),
    path(
        'collections/<str:name>/queryables/',
        views.pygeoapi_collection_queryables,
        name='pygeoapi-collection-queryable-list'
    ),
    path(
        'collections/<str:collection_id>/items/',
        views.get_pygeoapi_dataset_list,
        name='pygeoapi-collection-item-list'
    ),
    path(
        'collections/<str:collection_id>/items/<str:item_id>/',
        views.get_pygeoapi_dataset_detail,
        name='pygeoapi-collection-item-detail'
    ),
    path(
        'stac/',
        views.stac_catalog_root,
        name='pygeoapi-stac-catalog-root'
    ),
    path(
        'stac/<path:path>',
        views.stac_catalog_path_endpoint,
        name='pygeoapi-stac-catalog-path'
    ),
    path(
        'processes/',
        views.get_pygeoapi_processes,
        name='pygeoapi-process-list'
    ),
    path(
        'processes/<str:name>',
        views.get_pygeoapi_processes,
        name='pygeoapi-process-detail'
    ),
]