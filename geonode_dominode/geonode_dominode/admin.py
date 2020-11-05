from django.contrib import admin
from geonode.groups.models import GroupProfile
from guardian.admin import GuardedModelAdmin


class GroupProfileAdmin(GuardedModelAdmin):
    pass


# we unregister the standard geonode GroupProfile admin and then replace it
# with our own, which is based on django-guardian (and allows setting object-
# level permissions
admin.site.unregister(GroupProfile)
admin.site.register(GroupProfile, GroupProfileAdmin)
