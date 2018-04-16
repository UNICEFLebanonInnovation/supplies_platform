__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from supplies_platform.partners.tasks import link_partner_to_partnership


class Command(BaseCommand):
    help = 'link_partner_to_partnership'

    def handle(self, *args, **options):
        link_partner_to_partnership()
