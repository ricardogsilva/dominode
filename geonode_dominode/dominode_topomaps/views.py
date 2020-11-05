import logging
import typing

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
)
from django.views import (
    generic,
    View
)
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from geonode.base.auth import get_or_create_token
from geonode.layers.views import layer_detail as geonode_layer_detail

from .models import PublishedTopoMapIndexSheetLayer
from . import utils

logger = logging.getLogger(__name__)


def layer_detail(
        request,
        layername,
        template='layers/layer_detail.html'
):
    """Override geonode default layer detail view

    This view overrides geonode's default layer detail view in order to add
    additional topomap-related data to the render context. This is done in
    order to show a list of existing topomap sheets

    Implementation is a bit unusual:

    - first we call the original geonode view
    - we grab the response and extract the original context from it
    - then we figure out if we need to add topomap-related information to the
      context and proceed to do so if necessary
    - finally we render a response similar to what the original geonode view
      does, but we pass it our custom template

    """

    default_response: TemplateResponse = geonode_layer_detail(
        request, layername, template=template)
    context = default_response.context_data
    layer = context.get('resource')
    try:
        topomap = PublishedTopoMapIndexSheetLayer.objects.get(pk=layer.id)
    except PublishedTopoMapIndexSheetLayer.DoesNotExist:
        context['topomap'] = None
    else:
        context['topomap'] = topomap
        sheets_info = _get_topomap_sheets(topomap)
        context['sheets'] = sheets_info
    logger.debug('inside custom layer_detail view')
    logger.debug(f'context: {context}')
    return TemplateResponse(request, template, context=context)


class TopoMapLayerMixin:

    def get_object(self, queryset=None):
        queryset = queryset if queryset is not None else self.get_queryset()
        version = self.kwargs.get('version')
        series = self.kwargs.get('series')
        if version is None or series is None:
            raise AttributeError(
                f'Generic detail view {self.__class__.__name__} must be '
                f'called with a suitable version and series parameters in the '
                f'URLconf'
            )
        queryset = queryset.filter(
            name__contains=version).filter(name__contains=series)
        return get_object_or_404(queryset)


class TopomapListView(generic.ListView):
    queryset = PublishedTopoMapIndexSheetLayer.objects.all()
    template_name = 'dominode_topomaps/topomap-list.html'
    context_object_name = 'topomaps'
    paginate_by = 20


# this is currently unused, left here for future reference, in case we decide
# to provide a detail view for topomaps
class TopomapDetailView(TopoMapLayerMixin, generic.DetailView):
    model = PublishedTopoMapIndexSheetLayer
    template_name = 'dominode_topomaps/topomap-detail.html'
    context_object_name = 'topomap'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sheets_info = _get_topomap_sheets(self.object)
        context['sheets'] = sheets_info
        return context


class SheetDetailView(TopoMapLayerMixin, generic.DetailView):
    model = PublishedTopoMapIndexSheetLayer
    template_name = 'dominode_topomaps/topomap-sheet-detail.html'
    context_object_name = 'layer'

    def get(
            self,
            request: HttpRequest,
            sheet: str,
            *args,
            **kwargs
    ):
        self.object = self.get_object()
        can_download = self.request.user.has_perm(
            'download_resourcebase', self.object.resourcebase_ptr)

        sheet_paths = utils.find_sheet(
            self.object.series, self.object.version, sheet) or {}

        context = self.get_context_data(
            object=self.object,
            sheet=sheet,
            paper_sizes=sheet_paths.keys(),
            can_download=can_download
        )
        return self.render_to_response(context)


class TopomapSheetDownloadView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(
            self,
            request: HttpRequest,
            version: str,
            series: int,
            sheet: str,
            paper_size: str,
            *args,
            **kwargs
    ):
        queryset = PublishedTopoMapIndexSheetLayer.objects.filter(
            name__contains=version).filter(name__contains=series)
        topomap_layer = get_object_or_404(queryset)
        logger.debug(f'topomap_layer: {topomap_layer}')
        can_download = self.request.user.has_perm(
            'download_resourcebase', topomap_layer.resourcebase_ptr)
        if not can_download:
            raise Http404()
        else:
            available_sheet_paths = utils.find_sheet(series, version, sheet) or {}
            sheet_path = available_sheet_paths.get(paper_size)
            if sheet_path is not None:
                return FileResponse(
                    open(sheet_path, 'rb'),
                    as_attachment=True,
                    filename=sheet_path.name
                )
            else:
                raise Http404()


def _get_topomap_sheets(
        topomap: PublishedTopoMapIndexSheetLayer
) -> typing.List:
    geoserver_admin_user = get_user_model().objects.get(
        username=settings.OGC_SERVER_DEFAULT_USER)
    access_token = get_or_create_token(geoserver_admin_user)
    published_sheets = topomap.get_published_sheets(
        use_public_wfs_url=False, geoserver_access_token=access_token)
    sheets_info = []
    for sheet_index in published_sheets:
        sheet_paths = utils.find_sheet(
            topomap.series, topomap.version, sheet_index)
        if sheet_paths is not None:
            sheets_info.append({
                'index': sheet_index,
                'paper_sizes': sheet_paths.keys()
            })
    sheets_info = sorted(sheets_info, key=lambda x: x['index'])
    return sheets_info
