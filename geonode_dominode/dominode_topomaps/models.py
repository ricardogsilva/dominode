import re
import typing
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.db import models
from geonode.layers.models import Layer
from oauth2_provider.models import AccessToken


class PublishedTopomapsManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            title__contains=settings.DOMINODE_PUBLISHED_TOPOMAPS[
                'index_pattern']
        )


class PublishedTopoMapIndexSheetLayer(Layer):
    objects = PublishedTopomapsManager()

    class Meta:
        proxy = True

    @property
    def series(self):
        name_re_obj = re.search(
            'series-(\d+)', self._get_name_sections()['name'])
        return name_re_obj.group(1) if name_re_obj is not None else None

    @property
    def version(self):
        return self._get_name_sections()['version']

    def _get_name_sections(self):
        sections = self.name.split('_')
        return {
            'department': sections[0],
            'name': sections[1],
            'version': sections[2][1:]
        }

    def get_wfs_url(
            self,
            public: bool = True
    ) -> str:
        wfs_link = self.link_set.filter(name__iexact='geojson').first()
        if public:
            result = wfs_link.url
        else:
            wfs_base_url = urlparse(wfs_link.url).netloc
            internal_geoserver_base_url = urlparse(
                settings.GEOSERVER_LOCATION).netloc
            result = wfs_link.url.replace(
                wfs_base_url, internal_geoserver_base_url)
        return result

    def get_published_sheets(
            self,
            use_public_wfs_url: bool = True,
            geoserver_access_token: typing.Optional[AccessToken] = None
    ) -> typing.List[str]:
        wfs_url = self.get_wfs_url(public=use_public_wfs_url)
        if geoserver_access_token is not None:
            wfs_url += f'&access_token={geoserver_access_token.token}'
        ds = DataSource(wfs_url)
        wfs_layer = ds[0]
        return [feat.get('Index') for feat in wfs_layer]