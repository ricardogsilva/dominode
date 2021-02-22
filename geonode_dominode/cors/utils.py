import json
import os
import re
import sys
from datetime import datetime
from zipfile import ZipFile


class IndexedEntry:

    def __init__(
            self,
            archive_path,
            filename,
            year,
            date,
            hour,
            minute,
            utc_timestamp,
            size):
        self.archive_path = archive_path
        self.filename = filename
        self.year = year
        self.date = date
        self.hour = hour
        self.minute = minute
        self.utc_timestamp = utc_timestamp
        self.size = size

    def as_dict(self):
        return {
            'filename': self.filename,
            'year': self.year,
            'date': self.date,
            'hour': self.hour,
            'minute': self.minute,
            'utc_timestamp': self.utc_timestamp,
            'size': self.size
        }


class IndexedZipCollection:

    def __init__(self, search_path):
        self.search_path = search_path
        self.collection = []

    def index_directories(self):
        filename_pattern = re.compile(
            r'(.*)_(.*)_'
            r'(?P<year>\d{4})(?P<date>\d{3})(?P<hour>\d{2})(?P<minute>\d{2})')
        for root, dirs, files in os.walk(self.search_path):
            for archive_path in files:
                is_zip_file = archive_path.endswith('.zip')
                if not is_zip_file:
                    continue
                full_archive_path = os.path.join(root, archive_path)
                with ZipFile(full_archive_path) as zipf:
                    for info in zipf.infolist():
                        filename = info.filename
                        match = filename_pattern.match(filename)
                        year = match.group('year')
                        # this is a julian date
                        date = match.group('date')
                        hour = match.group('hour')
                        minute = match.group('minute')

                        utc_timestamp = datetime.strptime(
                            '{year}-{date}-{hour}-{minute}'.format(
                                year=year,
                                date=date,
                                hour=hour,
                                minute=minute
                            ), '%Y-%j-%H-%M')

                        entry = IndexedEntry(
                            archive_path=archive_path,
                            filename=filename,
                            year=year,
                            date=date,
                            hour=hour,
                            minute=minute,
                            utc_timestamp=utc_timestamp.isoformat(),
                            size=info.file_size)

                        self.collection.append(entry.as_dict())

    def as_json(self):
        return json.dumps(self.collection, indent=2)

    def write_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.collection, f, indent=2)

