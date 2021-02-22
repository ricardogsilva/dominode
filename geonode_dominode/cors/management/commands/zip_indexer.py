from django.core.management.base import BaseCommand, CommandError
from cors.utils import IndexedEntry, IndexedZipCollection


class Command(BaseCommand):
    help = 'Index files inside zip in a JSON format'

    def add_arguments(self, parser):
        parser.add_argument('search_path', type=str)
        parser.add_argument(
            '--output',
            type=str)

    def handle(self, *args, **options):
        search_path = options.get('search_path')
        output_path = options.get('output')
        zip_coll = IndexedZipCollection(search_path)
        zip_coll.index_directories()
        if output_path:
            zip_coll.write_to_json(output_path)
        else:
            self.stdout.write(zip_coll.as_json())
