# coding: utf-8
import django_tables2 as tables
from django.utils.translation import ugettext as _

from .models import SMVisit


class BootstrapTable(tables.Table):

    class Meta:
        model = SMVisit
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class SMVisitTable(tables.Table):

    partner = tables.Column(verbose_name='Partner', orderable=False, accessor='supply_plan_partner')
    partnership = tables.Column(verbose_name='Partnership', orderable=False, accessor='supply_plan_partnership')
    section = tables.Column(verbose_name='Section', orderable=False, accessor='supply_plan_section')
    assign_to_tpm = tables.Column(verbose_name='Assign to TPM', orderable=False, accessor='supply_plan_tpm')

    assessment = tables.TemplateColumn(verbose_name='Assessment', orderable=False,
                                                template_name='tpm/quantity_assessment.html',
                                                attrs={'url': '/tpm/visits/'})
    assign_to = tables.TemplateColumn(verbose_name='Assign to me', orderable=False,
                                        template_name='tpm/assign_to.html',
                                        attrs={'url': '/tpm/visits/'})

    class Meta:
        model = SMVisit
        fields = (
            'assign_to',
            'partner',
            'partnership',
            'section',
            'site',
            'supply_item',
            'quantity_distributed',
            'distribution_date',
            'assessment',
        )


class TPMVisitTable(tables.Table):

    partner = tables.Column(verbose_name='Partner', orderable=False, accessor='supply_plan_partner')
    partnership = tables.Column(verbose_name='Partnership', orderable=False, accessor='supply_plan_partnership')
    section = tables.Column(verbose_name='Section', orderable=False, accessor='supply_plan_section')
    assign_to_tpm = tables.Column(verbose_name='Assign to TPM', orderable=False, accessor='supply_plan_tpm')

    assessment = tables.TemplateColumn(verbose_name='Quality Assessment', orderable=False,
                                               template_name='tpm/quantity_assessment.html',
                                               attrs={'url': '/tpm/visits/'})
    assign_to = tables.TemplateColumn(verbose_name='Assign to me', orderable=False,
                                        template_name='tpm/assign_to.html',
                                        attrs={'url': '/tpm/visits/'})

    class Meta:
        model = SMVisit
        fields = (
            'assign_to',
            'partner',
            'partnership',
            'section',
            'site',
            'supply_item',
            'quantity_distributed',
            'distribution_date',
            'assessment',
        )
