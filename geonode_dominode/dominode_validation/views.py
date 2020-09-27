from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import generic

from . import models


class DominodeResourceListView(LoginRequiredMixin, generic.ListView):
    queryset = models.DominodeResource.objects.all().order_by('name')
    context_object_name = 'dominode_resources'
    paginate_by = 20


class DominodeResourceDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.DominodeResource
    context_object_name = 'resource'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_report'] = self.object._get_latest_report()
        threshold = 6
        context['other_recent_reports'] = (
            self.object.validation_reports.order_by('-created')[1:threshold]
        )
        context['show_all_reports'] = (
                self.object.validation_reports.count() >= threshold)
        return context


class ValidationReportListView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'validation_reports'
    paginate_by = 20

    def get_queryset(self):
        self.resource = get_object_or_404(
            models.DominodeResource, pk=self.kwargs['resource'])
        return models.ValidationReport.objects.filter(resource=self.resource)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource'] = self.resource
        return context


class ValidationReportDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.ValidationReport
    context_object_name = 'report'
