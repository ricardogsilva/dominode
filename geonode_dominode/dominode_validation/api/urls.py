from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(f'dominode-resources', views.DominodeResourceViewSet)
router.register(f'validation-reports', views.ValidationReportViewSet)
