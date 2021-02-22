import os
from zipfile import ZipFile

from django.conf import settings
from django.contrib.gis.db import models


class CORSStation(models.Model):
    """
    CORS Station
    """
    name = models.CharField(max_length=512, unique=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()

    def __str__(self):
        return self.name

    def indexes_in_zip_filename(self, date_from, date_to):
        cache_folder = os.path.join(settings.MEDIA_ROOT, 'cors')
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

        zip_file_name = '{}-{}-{}.zip'.format(
            self.name, date_from.strftime('%Y%m%d'), date_to.strftime('%Y%m%d'))
        # delete existing one
        zip_file = os.path.join(cache_folder, zip_file_name)
        if os.path.exists(zip_file):
            os.remove(zip_file)
        return zip_file

    def indexes_in_zip(self, date_from, date_to):
        """ Multi zip all file of index file in date range
        """
        indexes = self.indexfile_set.filter(
            date__gte=date_from, date__lt=date_to)
        zip_file = self.indexes_in_zip_filename(date_from, date_to)
        zip_object = ZipFile(zip_file, 'w')

        # let's copy every file to be zipped
        for index in indexes:
            path = index.get_local_path()
            if not path:
                continue
            zip_object.write(path, os.path.basename(path))

        zip_object.close()
        return zip_file

    def indexes_size(self, date_from, date_to):
        indexes = self.indexfile_set.filter(
            date__gte=date_from, date__lt=date_to)
        size = 0
        for index in indexes:
            size += index.file_size
        return size
