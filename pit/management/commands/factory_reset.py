from django.core.management.base import BaseCommand
from pit.utils import factory_reset


class Command(BaseCommand):
    """ Makes factory reset """
    help = 'Resets all data to default values'

    def handle(self, *args, **options):
        try:
            factory_reset()
            self.stdout.write(
                self.style.SUCCESS(
                    'All data was reset to default'
                )
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f'An error has occurred: {e}'
                )
            )
