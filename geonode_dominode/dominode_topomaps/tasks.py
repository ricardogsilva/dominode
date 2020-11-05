from celery.utils.log import get_task_logger
from django.template.loader import render_to_string
from geonode.layers.models import Layer

from geonode_dominode.celeryapp import app
from .models import PublishedTopoMapIndexSheetLayer

logger = get_task_logger(__name__)


@app.task(queue='geonode_dominode')
def add_custom_featureinfo_template_topomap():
    """
    Add custom featureinfo template to layers that represent published topomaps

    Published topomap layers feature download links that allow users to
    navigate to sheet detail page, where they may download individual topomap
    sheets. The default presentation of these links is just to render them as
    normal text. This task provides a custom representation that uses proper
    html anchor tags to render these download links as buttons.

    """

    for topomap_layer in PublishedTopoMapIndexSheetLayer.objects.all():
        layer: Layer = topomap_layer.layer
        if layer.featureinfo_custom_template in ('', None):
            logger.debug(
                f'Adding custom featureinfo template to '
                f'layer {layer!r}...'
            )
            rendered = render_to_string('dominode_topomaps/featureinfo.html')
            layer.featureinfo_custom_template = rendered
            layer.use_featureinfo_custom_template = True
            layer.save()
