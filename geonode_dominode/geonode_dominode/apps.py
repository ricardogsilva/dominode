# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2018 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
from django.apps import AppConfig as BaseAppConfig
import logging


logger = logging.getLogger('geonode_dominode')


def run_setup_hooks(*args, **kwargs):
    from django.conf import settings
    from .celeryapp import app as celeryapp
    if celeryapp not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += (celeryapp, )

    # Create new custom permission model
    try:
        from django.contrib.auth.models import ContentType, Permission
        from geonode.groups.models import GroupProfile
        group_content_type = ContentType.objects.get_for_model(GroupProfile)
        execute_sync_layers_perm, created = Permission.objects.get_or_create(
            codename='can_sync_geoserver',
            name='Can sync GeoServer',
            content_type=group_content_type
        )
        if created:
            logger.info('Created new permission: {}'.format(
                execute_sync_layers_perm))
    except BaseException:
        # The content type initialization must run after first database
        # initializations.
        pass


class AppConfig(BaseAppConfig):

    name = "geonode_dominode"
    label = "geonode_dominode"

    def ready(self):
        super(AppConfig, self).ready()
        run_setup_hooks()

