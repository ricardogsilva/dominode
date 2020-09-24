from django.urls import (
    include,
    path,
)

from .api.urls import router

urlpatterns = [
    path('api/', include(router.urls))
]