"""Integration of pygeoapi into DomiNode"""
import typing

from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse
)
from pygeoapi.api import API
from pygeoapi.openapi import get_oas

# TODO: test these views
# TODO: add authentication
# TODO: add authorization

def pygeoapi_root(request: HttpRequest) -> HttpResponse:
    pygeoapi_response = _get_pygeoapi_response(request, 'root')
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def pygeoapi_openapi_endpoint(request: HttpRequest) -> HttpResponse:
    openapi_config = get_oas(settings.PYGEOAPI_CONFIG)
    pygeoapi_response = _get_pygeoapi_response(
        request, 'openapi', openapi_config)
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def pygeoapi_conformance_endpoint(request: HttpRequest) -> HttpResponse:
    pygeoapi_response = _get_pygeoapi_response(request, 'conformance')
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def pygeoapi_collections_endpoint(
        request: HttpRequest,
        name: typing.Optional[str] = None,
) -> HttpResponse:
    pygeoapi_response = _get_pygeoapi_response(
        request, 'describe_collections', name)
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def pygeoapi_collection_queryables(
        request: HttpRequest,
        name: typing.Optional[str] = None,
) -> HttpResponse:
    pygeoapi_response = _get_pygeoapi_response(
        request, 'get_collection_queryables', name)
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def get_pygeoapi_dataset_list(
        request: HttpRequest,
        collection_id: str
) -> HttpResponse:
    pygeoapi_response = _get_pygeoapi_response(
        request, 'get_collection_items', collection_id)
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def get_pygeoapi_dataset_detail(
        request: HttpRequest,
        collection_id: str,
        item_id: str,
) -> HttpResponse:
    pygeoapi_response = _get_pygeoapi_response(
        request, 'get_collection_item', collection_id, item_id)
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def stac_catalog_root(request: HttpRequest) -> HttpResponse:
    pygeoapi_response = _get_pygeoapi_response(request, 'get_stac_root')
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def stac_catalog_path_endpoint(
        request: HttpRequest,
        path: str
) -> HttpResponse:
    pygeoapi_response = _get_pygeoapi_response(request, 'get_stac_path', path)
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def get_pygeoapi_processes(
        request: HttpRequest,
        name: typing.Optional[str] = None
) -> HttpResponse:
    pygeoapi_response = _get_pygeoapi_response(
        request, 'describe_processes', name)
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def _get_pygeoapi_response(
        request: HttpRequest,
        api_method_name: str,
        *args,
        **kwargs
) -> typing.Tuple[typing.Dict, int, str]:
    """Use pygeoapi to process the input request"""
    pygeoapi_api = API(settings.PYGEOAPI_CONFIG)
    api_method = getattr(pygeoapi_api, api_method_name)
    return api_method(request.headers, request.GET, *args, **kwargs)


def _convert_pygeoapi_response_to_django_response(
        pygeoapi_headers: typing.Mapping,
        pygeoapi_status_code: int,
        pygeoapi_content: str,
) -> HttpResponse:
    """Convert pygeoapi response to a django response"""
    response = HttpResponse(pygeoapi_content, status=pygeoapi_status_code)
    for key, value in pygeoapi_headers.items():
        response[key] = value
    return response
