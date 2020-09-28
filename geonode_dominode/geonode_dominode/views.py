import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.contrib.auth.models import Group
from django.http import (
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from geonode.groups import views
from geonode.groups.models import GroupProfile

from geonode_dominode.tasks import task_sync_geoserver

logger = logging.getLogger('geonode_dominode')


class GroupDetailView(views.GroupDetailView):
    """
    Mixes a detail view (the group) with a ListView (the members).
    """

    model = get_user_model()
    template_name = "groups/group_detail_override.html"
    paginate_by = None
    group = None

    def get_context_data(self, **kwargs):
        # data structure so the permission check is similar with django
        # template:
        # group_permissions.app_label.perm_codename will return true if
        # the this currently inspected group object has this permission.
        group_permissions = {
            p.content_type.app_label: {p.codename: True}
            for p in self.group.group.permissions.all()
            if p.content_type and p.content_type.app_label and p.codename
        }
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        context.update({'group_permissions': group_permissions})
        return context

    def get(self, request, *args, **kwargs):
        self.group = get_object_or_404(
            GroupProfile, slug=kwargs.get('slug'))
        response = super(GroupDetailView, self).get(request, *args, **kwargs)
        return response


@login_required
@permission_required('groups.can_sync_geoserver')
def sync_geoserver(request):
    """
    :type request: django.http.HttpRequest
    """
    if request.method == 'POST':
        user = request.user.get_username()
        group_slug = request.POST.get('group-slug')
        current_group = get_object_or_404(Group, name=group_slug)
        if not user.is_member_of_group(current_group):
            return HttpResponseNotAllowed()
        workspace_name = group_slug.replace('-editor', '')
        redirect = request.POST.get('redirect')
        logger.debug('Receiving GeoServer sync requests.')
        logger.debug('Group name: {}'.format(group_slug))
        logger.debug('Workspace name: {}'.format(workspace_name))
        logger.debug('User name: {}'.format(user))
        task_sync_geoserver.delay(workspace_name, user)
        messages.success(
            request, _(
                'GeoServer layers are being synced in the background. '
                'This process may take a while to complete. '
                'You will be notified via email when it is done.'))
        return HttpResponseRedirect(redirect_to=redirect)
    return HttpResponseBadRequest()
