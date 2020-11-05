from django.urls import (
    include,
    path,
)
from django.conf.urls import url
from django.views.generic import TemplateView, RedirectView

from geonode.urls import urlpatterns
from geonode.monitoring import register_url_event

from dominode_validation import urls as dominode_validation_urls
from dominode_topomaps import urls as dominode_topomaps_urls
from dominode_topomaps.views import layer_detail

from .views import (
    GroupDetailView,
    sync_geoserver,
)

homepage = register_url_event()(TemplateView.as_view(
    template_name='site_index.html'))

urlpatterns = [
    url(r'^/?$', homepage, name='home'),
    url(
        r'^groups/group/(?P<slug>[-\w]+)/$',
        GroupDetailView.as_view(),
        name='group_detail'
    ),
    path(
        'groups/group/<slug:group_slug>/sync_geoserver/',
        sync_geoserver,
        name='sync_geoserver'
    ),
    path('dominode-validation/', include(dominode_validation_urls)),
    path('dominode-topomaps/', include(dominode_topomaps_urls)),
    # overriding some of the default geonode layers views below
    url(r'^layers/(?P<layername>[^/]+)$', layer_detail, name="layer_detail"),
    url(r'^layers/upload$', RedirectView.as_view(url='/')),
    url(r'^layers/(?P<layername>[^/]*)/replace$',
        RedirectView.as_view(url='/')),
 ] + urlpatterns
