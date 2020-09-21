from django.views.generic.base import TemplateView


class MapView(TemplateView):
    template_name = 'cors/map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
