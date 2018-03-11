__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from supplies_platform.partners.tasks import sync_partner_data


class Command(BaseCommand):
    help = 'sync_partner_data'

    def handle(self, *args, **options):
        sync_partner_data()
