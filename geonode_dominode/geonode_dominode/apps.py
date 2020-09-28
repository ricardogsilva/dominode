from django.apps import AppConfig as BaseAppConfig
import logging

from .constants import GEOSERVER_SYNC_PERM_CODE

logger = logging.getLogger(__name__)


def run_setup_hooks(*args, **kwargs):
    from django.conf import settings
    from .celeryapp import app as celeryapp
    if celeryapp not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += (celeryapp, )
    try:
        create_geoserver_sync_permission()
    except BaseException:
        # content type initialization must run after first db initializations
        pass


class AppConfig(BaseAppConfig):

    name = "geonode_dominode"
    label = "geonode_dominode"

    def ready(self):
        super(AppConfig, self).ready()
        run_setup_hooks()
        from . import signals


def create_geoserver_sync_permission():
    from django.contrib.auth.models import ContentType, Permission
    from geonode.groups.models import GroupProfile
    group_content_type = ContentType.objects.get_for_model(GroupProfile)
    perm, created = Permission.objects.get_or_create(
        codename=GEOSERVER_SYNC_PERM_CODE,
        name='Can sync GeoServer',
        content_type=group_content_type
    )
    if created:
        logger.info(f'Created new permission: {perm}')
    return perm