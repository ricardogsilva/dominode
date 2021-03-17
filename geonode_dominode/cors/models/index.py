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
    date = models.DateTimeField()
    file_name = models.CharField(
        max_length=512)
    location = models.CharField(
        max_length=512,
        default='http://bucket/cors/',
        help_text="Location Path in S3 bucket")
   
    class Meta:
        unique_together = ('file_name','location')
