import typing

from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse
)
from pygeoapi.api import API

# TODO: test these views
# TODO: add authentication
# TODO: add authorization

def pygeoapi_root(request: HttpRequest):
    pygeoapi_response = _get_pygeoapi_response(request, 'root')
    return _convert_pygeoapi_response_to_django_response(pygeoapi_response)


def stac_catalog_root(request: HttpRequest):
    pygeoapi_response = _get_pygeoapi_response(request, 'get_stac_root')
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def stac_catalog_path_endpoint(
        request: HttpRequest, path: typing.Optional[str] = None):
    pygeoapi_response = _get_pygeoapi_response(
        request, 'get_stac_path', path=path)
    return _convert_pygeoapi_response_to_django_response(*pygeoapi_response)


def _get_pygeoapi_response(
        request: HttpRequest,
        api_method_name: str,
        **kwargs
) -> typing.Tuple[typing.Dict, int, str]:
    """Use pygeoapi to process the input request"""
    pygeoapi_api = API(settings.PYGEOAPI_CONFIG)
    api_method = getattr(pygeoapi_api, api_method_name)
    return api_method(request.headers, request.get, **kwargs)


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
