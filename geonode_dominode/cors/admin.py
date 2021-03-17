from django.contrib import admin
from cors.models.index import IndexFile
from cors.models.station import CORSStation


def download_from_ftp(modeladmin, request, queryset):
    for object in queryset:
        object.check_file_path()


download_from_ftp.short_description = "Download file from ftp to local"


class IndexFileAdmin(admin.ModelAdmin):
    list_display = ('station','date','file_name','location')
    actions = [download_from_ftp]


admin.site.register(IndexFile, IndexFileAdmin)


class CORSStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'x', 'y', 'z')


admin.site.register(CORSStation, CORSStationAdmin)
