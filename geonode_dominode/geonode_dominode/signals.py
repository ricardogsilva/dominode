"""Signal handlers for Dominode"""

import logging
import typing

from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from .constants import GEOSERVER_SYNC_PERM_CODE

logger = logging.getLogger(__name__)

@receiver(
    post_save,
    sender=Group,
    dispatch_uid='assign_geoserver_sync_permission_uid'
)
def check_assign_geoserver_sync_permission(
        sender: typing.Type,
        instance: Group,
        created: bool,
        **kwargs
):
    """Assign GeoServer sync perm when a suitable Group instance is created."""
    if created and instance.name.endswith('-editor'):
        logger.debug(f'Assigning geoserver sync permission to {instance}...')
        assign_perm(GEOSERVER_SYNC_PERM_CODE, instance)
