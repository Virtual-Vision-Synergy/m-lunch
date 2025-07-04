# Management Command pour remplacer script-reset.sql
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = 'Reset database and load initial data'

    def handle(self, *args, **options):
        self.stdout.write('Resetting database...')

        # Reset migrations
        call_command('migrate', 'core', 'zero')
        call_command('migrate', 'backoffice', 'zero')
        call_command('migrate', 'frontoffice', 'zero')

        # Re-apply migrations
        call_command('migrate')

        # Load initial data
        call_command('loaddata', 'initial_statuts')
        call_command('loaddata', 'initial_zones')

        self.stdout.write(
            self.style.SUCCESS('Database reset successfully!')
        )
