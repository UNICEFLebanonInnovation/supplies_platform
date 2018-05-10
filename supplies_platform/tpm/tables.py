# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import TPMVisit


class BootstrapTable(tables.Table):

    class Meta:
        model = TPMVisit
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class TPMVisitTable(tables.Table):

    class Meta:
        model = TPMVisit
        fields = (
            'supply_plan_partner',
            'supply_plan_partnership',
            'supply_plan_section',
            'site',
            'supply_item',
            'quantity_distributed',
            'distribution_date',
        )
