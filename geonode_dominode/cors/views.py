from django.views.generic.base import TemplateView

class MapView(TemplateView):
    template_name = 'cors/map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_download_observation_permission'] = \
            self.request.user.is_authenticated and self.request.user.has_perm('cors.download_observation')
        return context