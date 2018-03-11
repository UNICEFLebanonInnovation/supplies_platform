
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin

from .models import PartnerOrganization


class PartnerOrganizationResource(resources.ModelResource):
    class Meta:
        model = PartnerOrganization
        fields = (
            'id',
            'vendor_number',
            'name',
            'short_name',
            'partner_type',
            'cso_type',
            'rating',
            'shared_partner',
            'email',
            'phone_number',
        )
        export_order = fields


class PartnerOrganizationAdmin(ImportExportModelAdmin):
    resource_class = PartnerOrganizationResource


admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)
