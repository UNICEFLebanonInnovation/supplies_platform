from supplies_platform.taskapp.celery import app

import json
import httplib
import datetime
from time import mktime
from supplies_platform.backends.utils import get_data


@app.task
def sync_partner_data():
    from supplies_platform.partners.models import PartnerOrganization
    partners = get_data('etools.unicef.org', '/api/v2/partners/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')
    partners = json.loads(partners)
    for item in partners:
        partner, new_instance = PartnerOrganization.objects.get_or_create(id=item['id'])

        partner.rating = item['rating']
        partner.short_name = item['short_name']
        partner.vendor_number = item['vendor_number']
        partner.phone_number = item['phone_number']
        partner.partner_type = item['partner_type']
        partner.name = item['name']
        partner.email = item['email']
        partner.street_address = item['street_address']

        partner.save()


@app.task
def sync_agreement_data():
    from supplies_platform.partners.models import Agreement, PartnerOrganization
    partners = get_data('etools.unicef.org', '/api/v2/agreements/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')

    partners = json.loads(partners)
    for item in partners:
        partner, new_instance = Agreement.objects.get_or_create(id=item['id'])

        partner.partner_id = item['partner']
        partner.country_programme = item['country_programme']
        partner.agreement_number = item['agreement_number']
        partner.agreement_type = item['agreement_type']
        partner.end = item['end']
        partner.start = item['start']
        partner.signed_by_unicef_date = item['signed_by_unicef_date']
        partner.signed_by_partner_date = item['signed_by_partner_date']
        partner.status = item['status']
        partner.agreement_number_status = item['agreement_number_status']

        partner.save()


@app.task
def sync_intervention_data():
    from supplies_platform.partners.models import PCA
    from supplies_platform.locations.models import Location
    partners = get_data('etools.unicef.org', '/api/v2/interventions/', 'Token 36f06547a4b930c6608e503db49f1e45305351c2')

    partners = json.loads(partners)
    for item in partners:
        partner, new_instance = PCA.objects.get_or_create(id=item['id'])

        partner.number = item['number']
        partner.document_type = item['document_type']
        partner.partner_name = item['partner_name']
        partner.status = item['status']
        partner.title = item['title']
        partner.start = item['start']
        partner.end = item['end']
        partner.end_date = item['end']
        # partner.sections = item['sections']
        # partner.section_names = item['section_names']
        # partner.offices = item['offices']

        partner.save()


@app.task
def sync_individual_intervention_data(partner=None):
    from supplies_platform.partners.models import Agreement, PartnerOrganization, PCA
    interventions = PCA.objects.all()

    for partner in interventions:
        item = get_data('etools.unicef.org', '/api/v2/interventions/{}/'.format(partner.id),
                        'Token 36f06547a4b930c6608e503db49f1e45305351c2')

        try:
            item = json.loads(item)

            partner.partner_id = item['partner_id']
            partner.agreement_id = item['agreement']
            partner.number = item['number']
            partner.document_type = item['document_type']
            partner.status = item['status']
            partner.title = item['title']
            partner.start = item['start']
            partner.end = item['end']
            partner.end_date = item['end']
            partner.save()
        except Exception as ex:
            print(item)
            print(ex.message)
            continue


def link_partner_to_partnership():
    from supplies_platform.partners.models import PartnerOrganization, PCA

    partnerships = PCA.objects.all()

    for pca in partnerships:
        try:
            partner = PartnerOrganization.objects.get(name=pca.partner_name)
            pca.partner = partner
            pca.save()
        except Exception as ex:
            continue
