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

    def indexes_in_txt_filename(self, date_from, date_to):
        cache_folder = os.path.join(settings.MEDIA_ROOT, 'cors')
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

        txt_file_name = '{}-{}-{}.txt'.format(
            self.name, date_from.strftime('%Y%m%d'), date_to.strftime('%Y%m%d'))
        # delete existing one
        txt_file = os.path.join(cache_folder, txt_file_name)
        if os.path.exists(txt_file):
            os.remove(txt_file)
        return txt_file

    def indexes_in_txt(self, date_from, date_to):
        """ Multi zip all file of index file in date range
        """
        indexes = self.indexfile_set.filter(
            date__gte=date_from, date__lt=date_to).order_by('date')
        txt_file = self.indexes_in_txt_filename(date_from, date_to)
        list_file = list()
        list_dates = list()
        for index in indexes:
            list_file.append(index.location)
            list_dates.append(index.date)
        with open(txt_file, 'w') as f:
            for i in range(len(list_file)) :
                f.write("{}  {}\n".format(list_dates[i],list_file[i]))
        return txt_file

    def get_indexes(self, date_from, date_to):
        indexes = self.indexfile_set.filter(
            date__gte=date_from, date__lt=date_to).order_by('date')
        return indexes
