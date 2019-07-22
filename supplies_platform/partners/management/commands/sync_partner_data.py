__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from supplies_platform.partners.tasks import (
    sync_partner_data,
    sync_agreement_data,
    sync_intervention_data,
    sync_individual_intervention_data
)


class Command(BaseCommand):
    help = 'sync_partner_data'

    def handle(self, *args, **options):
        sync_partner_data()
        sync_agreement_data()
        sync_intervention_data()
        sync_individual_intervention_data()
