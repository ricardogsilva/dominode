import os
from django.contrib.gis.db import models
from cors.middleware.ftp_connection import IndexFileFTP
from cors.models.station import CORSStation


class IndexFile(IndexFileFTP, models.Model):
    """
    Index file from ftp,
    so we can filter it fast and just download necessary files

    It can be searched by
    - if it has zip file, open the zip and check file with the file_path in there
    """
    station = models.ForeignKey(CORSStation, on_delete=models.CASCADE)

    file_name = models.CharField(
        max_length=512)
    ftp_file_path = models.CharField(
        max_length=512,
        help_text="The actual path of the actual file. Can be in zip.")
    ftp_zip_path = models.CharField(
        max_length=512, null=True, blank=True,
        help_text="The actual zip path if filename is in a zip file.")

    # this is saved after downloaded as local
    local_path = models.CharField(
        max_length=512, null=True, blank=True,
        help_text="The actual path of the file in local after downloaded in local.")

    # the properties
    file_size = models.BigIntegerField(
        help_text='Size in byte'
    )
    date = models.DateField()

    def __str__(self):
        if self.ftp_zip_path:
            return '{} in zip {}'.format(self.file_name, self.ftp_zip_path)
        else:
            return '{} with path {}'.format(self.file_name, self.ftp_file_path)

    class Meta:
        unique_together = ('file_name', 'ftp_file_path', 'ftp_zip_path')

    def get_local_path(self):
        """ Return local path, if not in the local, downlaod it """
        if self.local_path and os.path.exists(self.local_path):
            return self.local_path
        elif self.ftp_zip_path:
            self.local_path = self.download_zip(
                self.ftp_file_path, self.ftp_zip_path)
            self.save()
            return self.local_path
        return None
