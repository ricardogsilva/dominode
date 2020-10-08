"""Extra context processors for DomiNode

These add stuff to the context that is available for all templates

"""

import typing

from django.http import HttpRequest

from .constants import GEOSERVER_SYNC_CATEGORY_NAME


def user_is_geoserver_editor(request: HttpRequest) -> typing.Dict:
    if request.user.is_authenticated:
        has_editor_category = request.user.groupmember_set.filter(
            group__categories__name=GEOSERVER_SYNC_CATEGORY_NAME).exists()
    else:
        has_editor_category = False
    return {
        'user_is_geoserver_editor': has_editor_category
    }