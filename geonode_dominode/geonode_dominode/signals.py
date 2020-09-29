"""Signal handlers for Dominode"""

import logging
import typing

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from geonode.groups.models import GroupProfile
from guardian.shortcuts import assign_perm

from .constants import GEOSERVER_SYNC_PERM_CODE

logger = logging.getLogger(__name__)

@receiver(
    m2m_changed,
    sender=GroupProfile.categories.through,
    dispatch_uid='assign_geoserver_sync_permission_uid'
)
def check_assign_geoserver_sync_permission(
        sender: typing.Type,
        instance: GroupProfile,
        action: str,
        reverse: bool,
        **kwargs
):
    """Assign GeoServer sync perm when a suitable Group instance is created."""
    if action == 'post_add':
        existing_categories = [cat.name for cat in instance.categories.all()]
        if instance.categories.filter(name='dominode-editor').exists():
            group = instance.group
            logger.debug(
                f'Assigning geoserver sync permission to group {group}...')
            assign_perm(
                f'groups.{GEOSERVER_SYNC_PERM_CODE}', group, instance)
