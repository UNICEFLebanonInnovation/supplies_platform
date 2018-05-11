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

    partner = tables.Column(verbose_name='Partner', orderable=False, accessor='supply_plan_partner')
    partnership = tables.Column(verbose_name='Partnership', orderable=False, accessor='supply_plan_partnership')
    section = tables.Column(verbose_name='Section', orderable=False, accessor='supply_plan_section')

    quantity_assessment = tables.TemplateColumn(verbose_name='Quantity Assessment', orderable=False,
                                                template_name='tpm/quantity_assessment.html',
                                                attrs={'url': '/tpm/visits/'})
    quality_assessment = tables.TemplateColumn(verbose_name='Quality Assessment', orderable=False,
                                               template_name='tpm/quality_assessment.html',
                                               attrs={'url': '/tpm/visits/'})
    assign_to = tables.TemplateColumn(verbose_name='Assign to me', orderable=False,
                                        template_name='tpm/assign_to.html',
                                        attrs={'url': '/tpm/visits/'})
    assign_to_tpm = tables.TemplateColumn(verbose_name='Assign to TPM', orderable=False,
                                        template_name='tpm/assign_to_tpm.html',
                                        attrs={'url': '/tpm/visits/'})

    class Meta:
        model = TPMVisit
        fields = (
            'assign_to',
            'assign_to_tpm',
            'partner',
            'partnership',
            'section',
            'site',
            'supply_item',
            'quantity_distributed',
            'distribution_date',
            'quantity_assessment',
            'quality_assessment',
        )
