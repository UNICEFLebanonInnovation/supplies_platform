import datetime

from django.contrib import admin
from django import forms

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
import nested_admin

from supplies_platform.partners.models import PCA, PartnerStaffMember
from supplies_platform.users.util import has_group
from supplies_platform.supplies.models import SupplyItem
from .models import (
    SupplyPlan,
    WavePlan,
    SupplyPlanItem,
    DistributionPlan,
    DistributionPlanItem,
    DistributionPlanWave,
    DistributionPlanItemReceived,
)
from .forms import (
    SupplyPlanForm,
    WavePlanForm,
    WavePlanFormSet,
    DistributionPlanForm,
    DistributionPlanFormSet,
    DistributionPlanItemForm,
    DistributionPlanItemFormSet,
    DistributionPlanWaveForm,
    DistributionPlanWaveFormSet,
)


class WavePlanInline(nested_admin.NestedStackedInline):
    model = WavePlan
    form = WavePlanForm
    formset = WavePlanFormSet
    verbose_name = 'Wave'
    verbose_name_plural = 'Waves'
    min_num = 0
    max_num = 4
    extra = 0
    fk_name = 'supply_plan'
    suit_classes = u'suit-tab suit-tab-waves'

    fields = (
        'wave_number',
        'quantity_required',
        'date_required_by',
    )


class SupplyPlanItemInline(nested_admin.NestedStackedInline):
    model = SupplyPlanItem
    verbose_name = 'Supply Item'
    verbose_name_plural = 'Supply Items'
    extra = 0
    fk_name = 'supply_plan'
    suit_classes = u'suit-tab suit-tab-waves'

    fields = (
        'item',
        'quantity',
        'item_price',
        'total_budget',
        'covered_per_item',
        'target_population',
    )

    inlines = [WavePlanInline, ]

    readonly_fields = (
        'item_price',
        'total_budget',
        'target_population',
        'covered_per_item',
    )


class SupplyPlanResource(resources.ModelResource):
    class Meta:
        model = SupplyPlan
        fields = (
            'pca',
            'partner',
            'section',
            'status',
            'created',
            'created_by',
            'approved',
        )
        export_order = fields


class SupplyPlanAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
    resource_class = SupplyPlanResource
    # form = SupplyPlanForm
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'section',
                'partner',
                'pca',
                'status',
                'comments',
                'partnership_start_date',
                'partnership_end_date',
                'total_budget',
                'created',
                'created_by',
            ]
        }),
        ('Review', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'reviewed',
                'review_date',
                'reviewed_by',
                'review_comments',
            ]
        }),
        ('Approval', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'approved',
                'approval_date',
                'approved_by',
                'approval_comments',
            ]
        }),
    ]

    suit_form_tabs = (
                      ('general', 'Supply Plan'),
                      ('waves', 'Supply Items'),
                    )

    inlines = [SupplyPlanItemInline, ]

    ordering = (u'-created',)
    date_hierarchy = u'created'
    search_fields = (
        'partner__name',
        'pca',
    )
    list_display = (
        'section',
        'partner',
        'pca',
        'partnership_start_date',
        'partnership_end_date',
        'status',
        'created',
        'created_by',
        'approval_date',
        'approved_by',
    )
    list_filter = (
        'partner',
        'status',
        'approved',
        'approved_by',
        'approval_date',
        'section',
    )

    # class Media:
    #     js = ('js/chainedfk.js', )

    def partnership_start_date(self, obj):
        if obj.pca:
            return obj.pca.start
        return ''

    def partnership_end_date(self, obj):
        if obj.pca:
            return obj.pca.end
        return ''

    def get_readonly_fields(self, request, obj=None):

        fields = [
            'partnership_start_date',
            'partnership_end_date',
            'status',
            'created',
            'created_by',
            'reviewed',
            'review_date',
            'reviewed_by',
            'review_comments',
            'approved',
            'approved_by',
            'approval_date',
            'approval_comments',
            'total_budget',
        ]

        if has_group(request.user, 'SUPPLY_FP') and obj and obj.status == obj.SUBMITTED:
            fields.remove('reviewed')
            fields.remove('review_comments')

        if has_group(request.user, 'BUDGET_OWNER') and obj and obj.status == obj.REVIEWED:
            fields.remove('approved')
            fields.remove('approval_comments')

        if has_group(request.user, 'UNICEF_PA'):
            fields.remove('status')

        return fields

    def get_form(self, request, obj=None, **kwargs):
        form = super(SupplyPlanAdmin, self).get_form(request, obj, **kwargs)
        form.request = request
        user = request.user
        form.base_fields['section'].initial = user.section
        if has_group(request.user, 'UNICEF_PA'):
            form.base_fields['status'].choices = (
                (SupplyPlan.DRAFT, u"Draft"),
                (SupplyPlan.PLANNED, u"Planned"),
                (SupplyPlan.SUBMITTED, u"Submitted"),
                (SupplyPlan.COMPLETED, u"Completed"),
                (SupplyPlan.CANCELLED, u"Cancelled"),
            )
        if has_group(request.user, 'BUDGET_OWNER') and 'approved_by' in form.base_fields:
            form.base_fields['approved_by'].initial = user

        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            obj.to_review = True
        if obj and obj.reviewed is True and not obj.review_date:
            obj.review_date = datetime.datetime.now()
            obj.reviewed_by = request.user
            obj.status = obj.REVIEWED
            obj.to_approve = True
        if obj and obj.approved is True and not obj.approval_date:
            obj.approval_date = datetime.datetime.now()
            obj.approved_by = request.user
            obj.status = obj.APPROVED
            DistributionPlan.objects.create(plan=obj)
        super(SupplyPlanAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(SupplyPlanAdmin, self).get_queryset(request)
        if has_group(request.user, 'UNICEF_PA'):
            qs = qs.filter(created_by=request.user)
        if has_group(request.user, 'BUDGET_OWNER'):
            qs = qs.filter(status__in=['reviewed', 'approved'])
        return qs


class DistributionPlanWaveInline(nested_admin.NestedStackedInline):
    model = DistributionPlanWave
    form = DistributionPlanWaveForm
    formset = DistributionPlanWaveFormSet
    verbose_name = 'Item'
    verbose_name_plural = 'Items'
    min_num = 0
    max_num = 99
    extra = 0
    fk_name = 'plan'
    suit_classes = u'suit-tab suit-tab-request'

    fields = (
        'supply_item',
        'quantity_required',
        # 'delivery_location',
        'date_distributed_by',
    )


class DistributionPlanItemInline(admin.StackedInline):
    model = DistributionPlanItem
    max_num = 99
    min_num = 0
    extra = 0
    verbose_name = 'Request per wave'
    verbose_name_plural = 'Requests per wave'
    form = DistributionPlanItemForm
    formset = DistributionPlanItemFormSet
    # fk_name = 'plan'
    suit_classes = u'suit-tab suit-tab-request'

    fields = (
        'wave_number',
        'wave',
        'site',
        'target_population',
        'delivery_location',
        'contact_person',
        'quantity_requested',
        'date_required_by',
        'date_distributed_by',
    )

    # inlines = [DistributionPlanWaveInline, ]


class ReceivedItemInline(admin.StackedInline):
    model = DistributionPlanItemReceived
    max_num = 99
    min_num = 0
    extra = 0
    verbose_name = 'Received items per wave'
    verbose_name_plural = 'Received items'
    suit_classes = u'suit-tab suit-tab-distribution'

    fields = (
        'wave_number',
        'wave',
        'quantity_received',
        'date_received',
        'quantity_balance',
        'date_distributed',
        # 'quantity_distributed'
    )

    readonly_fields = (
        'quantity_balance',
    )


class DistributionPlanResource(resources.ModelResource):
    class Meta:
        model = DistributionPlan
        fields = (
            'plan',
        )
        export_order = fields


class DistributionPlanAdmin(ImportExportModelAdmin):
    resource_class = DistributionPlanResource

    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'plan',
                'plan_partner',
                'plan_partnership',
                'plan_section',
                'status',
                'comments'
            ]
        }),
        ('Review', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'reviewed',
                'review_date',
                'reviewed_by',
                'review_comments',
            ]
        }),
        ('Approval', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'approved',
                'approved_by',
                'approval_date',
                'approval_comments',
            ]
        }),
    ]

    suit_form_tabs = (
                      ('general', 'Distribution Plan'),
                      ('request', 'Request Items Plan'),
                      ('distribution', 'Received Items'),
                    )

    search_fields = (
        'plan__partnership',
    )
    list_display = (
        'plan_partner',
        'plan_partnership',
        'plan_section',
        'status',
    )
    list_filter = (
        'status',
        'plan__partner',
        'plan__section',
    )

    inlines = [DistributionPlanItemInline, ReceivedItemInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super(DistributionPlanAdmin, self).get_form(request, obj, **kwargs)
        form.request = request
        user = request.user
        if has_group(request.user, 'PARTNER'):
            form.base_fields['status'].choices = (
                (DistributionPlan.DRAFT, u"Draft"),
                (DistributionPlan.PLANNED, u"Planned"),
                (DistributionPlan.SUBMITTED, u"Submitted"),
                (DistributionPlan.COMPLETED, u"Completed"),
                (DistributionPlan.CANCELLED, u"Cancelled"),
            )

        return form

    def get_readonly_fields(self, request, obj=None):

        fields = [
            'plan',
            'plan_partner',
            'plan_partnership',
            'plan_section',
            'status',
            'reviewed',
            'review_date',
            'reviewed_by',
            'review_comments',
            'approved',
            'approved_by',
            'approval_date',
            'approval_comments',
        ]

        if has_group(request.user, 'ZONAL_FP') and obj and obj.status == obj.SUBMITTED:
            fields.remove('reviewed')
            fields.remove('review_comments')

        if has_group(request.user, 'SUPPLY_FP') and obj and obj.status == obj.REVIEWED:
            fields.remove('approved')
            fields.remove('approval_comments')

        if has_group(request.user, 'PARTNER'):
            fields.remove('status')

        return fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            obj.to_review = True
        if obj and obj.reviewed is True and not obj.review_date:
            obj.review_date = datetime.datetime.now()
            obj.reviewed_by = request.user
            obj.status = obj.REVIEWED
            obj.to_approve = True
        if obj and obj.approved is True and not obj.approval_date:
            obj.approval_date = datetime.datetime.now()
            obj.approved_by = request.user
            obj.status = obj.APPROVED
        super(DistributionPlanAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(DistributionPlanAdmin, self).get_queryset(request)
        if has_group(request.user, 'PARTNER'):
            qs = qs.filter(plan__partner_id=request.user.partner_id)
        if has_group(request.user, 'FIELD_FP'):
            qs = qs.filter(status__in=['reviewed', 'submitted'])
        return qs


admin.site.register(SupplyPlan, SupplyPlanAdmin)
admin.site.register(DistributionPlan, DistributionPlanAdmin)

