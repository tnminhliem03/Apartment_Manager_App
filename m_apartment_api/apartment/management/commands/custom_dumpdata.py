import sys

from django.core.management.base import BaseCommand
from django.core.management import call_command
import codecs
from apartment.models import User, Resident

class Command(BaseCommand):
    def handle(self, *args, **options):
        output_filename = 'all_data.json'

        with codecs.open(output_filename, 'w', 'utf-8') as f:
            original_stdout = sys.stdout
            sys.stdout = f

            app_name = 'apartment'

            from django.apps import apps
            models = apps.get_app_config(app_name).get_models()

            for model in models:
                call_command('dumpdata', model._meta.label, indent=4,
                             use_natural_foreign_keys=True, use_natural_primary_keys=True)

            sys.stdout = original_stdout