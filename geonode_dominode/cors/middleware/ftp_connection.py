import ftputil
import os
import zipfile
from django.conf import settings


class IndexFileFTP(object):
    """
    Class contains communication to ftp with the index file
    """

    url = '199.189.115.66'
    username = 'cors'
    password = 'c0rs_dm'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_folder = os.path.join(settings.MEDIA_ROOT, 'cors_cache')
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

    def download_zip(self, file_path, zip_path):
        """ Download file in the zip file
        :return:
        """

        with ftputil.FTPHost(self.url, self.username, self.password) as host:
            if host.path.isfile(os.path.join(host.curdir, zip_path)):
                zip_file = os.path.join(
                    self.cache_folder, zip_path
                )
                # create folder for download
                downloaded_folder = os.path.dirname(zip_file)
                if not os.path.exists(downloaded_folder):
                    os.makedirs(downloaded_folder)

                # download zip file
                local_file = os.path.join(downloaded_folder, file_path)

                # if the local file is not exist, download the zip and unzip it
                if not os.path.exists(local_file):
                    if not os.path.exists(zip_file):
                        host.download(
                            zip_path, zip_file
                        )
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(downloaded_folder)

                    # delete the zip file
                    os.remove(zip_file)

                # return local file
                if os.path.exists(local_file):
                    return local_file
        return None
