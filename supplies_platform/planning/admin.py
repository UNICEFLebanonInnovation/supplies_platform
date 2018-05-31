import datetime

from django.contrib import admin
from django import forms
from django.db.models import Avg, Count, Min, Sum
from django.core.urlresolvers import resolve

from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
import nested_admin

from supplies_platform.backends.utils import send_notification
from supplies_platform.users.util import has_group
from .models import (
    SupplyPlan,
    WavePlan,
    SupplyPlanItem,
    DistributionPlan,
    DistributionPlanItem,
    DistributionPlanItemReceived,
    DistributedItem,
    DistributedItemSite,
)
from .forms import (
    SupplyPlanForm,
    WavePlanForm,
    WavePlanFormSet,
    DistributionPlanForm,
    DistributionPlanItemForm,
    DistributionPlanItemFormSet,
    DistributionItemForm,
    DistributionItemFormSet,
    DistributedItemSiteForm,
    DistributedItemSiteFormSet,
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
        'beneficiaries_covered_per_item',
        # 'target_population',
    )

    inlines = [WavePlanInline, ]

    readonly_fields = (
        'item_price',
        'total_budget',
        # 'target_population',
        'beneficiaries_covered_per_item',
    )

    # def get_readonly_fields(self, request, obj=None):
    #     if has_group(request.user, 'UNICEF_PD') and obj and obj.status in ['SUBMITTED', 'APPROVED']:
    #         return self.fields
    #     return self.readonly_fields
    #
    # def has_add_permission(self, request, obj=None):
    #     if has_group(request.user, 'UNICEF_PD') and obj and obj.plan.status in ['SUBMITTED', 'APPROVED']:
    #         return False
    #     return True
    #
    # def has_change_permission(self, request, obj=None):
    #     if has_group(request.user, 'UNICEF_PD') and obj and obj.plan.status in ['SUBMITTED', 'APPROVED']:
    #         return False
    #     return True


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
    form = SupplyPlanForm
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'reference_number',
                'section',
                'partner',
                'pca',
                'status',
                'tpm_focal_point',
                'comments',
                'partnership_start_date',
                'partnership_end_date',
                'total_budget',
                'target_population',
                'created',
                'created_by',
                'submission_date',
            ]
        }),
        ('Review by UNICEF Supply Beirut focal point', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'reviewed',
                'review_date',
                'reviewed_by',
                'review_comments',
            ]
        }),
        ('Approval by UNICEF budget owner', {
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
        'reference_number',
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
            'reference_number',
            'partnership_start_date',
            'partnership_end_date',
            'status',
            'created',
            'created_by',
            'submission_date',
            'reviewed',
            'review_date',
            'reviewed_by',
            'review_comments',
            'approved',
            'approved_by',
            'approval_date',
            'approval_comments',
            'total_budget',
            'target_population',
        ]

        if has_group(request.user, 'SUPPLY_FP') and obj and obj.status == obj.SUBMITTED:
            fields.remove('reviewed')
            fields.remove('review_comments')

        if has_group(request.user, 'BUDGET_OWNER') and obj and obj.status == obj.REVIEWED:
            fields.remove('approved')
            fields.remove('approval_comments')

        if has_group(request.user, 'UNICEF_PD'):
            fields.remove('status')

        return fields

    def get_form(self, request, obj=None, **kwargs):
        form = super(SupplyPlanAdmin, self).get_form(request, obj, **kwargs)
        form.request = request
        user = request.user
        form.base_fields['section'].initial = user.section
        if has_group(request.user, 'UNICEF_PD'):
            form.base_fields['status'].choices = (
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
        if obj and obj.status == obj.SUBMITTED and not obj.submission_date:
            obj.submission_date = datetime.datetime.now()
            obj.to_review = True
            send_notification('SUPPLY_ADMIN', 'SUPPLY PLAN SUBMITTED - TO REVIEW BY SUPPLY', obj)
        if obj and 'reviewed' in request.POST and not obj.review_date:
            if obj.reviewed is True:
                obj.review_date = datetime.datetime.now()
                obj.reviewed_by = request.user
                obj.status = obj.REVIEWED
                obj.to_approve = True
                send_notification('UNICEF_PD', 'SUPPLY PLAN REVIEWED BY SUPPLY', obj)
                send_notification('BUDGET_OWNER', 'SUPPLY PLAN TO APPROVE BY THE BUDGET OWNER', obj)
            elif obj.reviewed is False:
                obj.status = obj.PLANNED
                obj.submission_date = None
                send_notification('UNICEF_PD', 'SUPPLY PLAN REJECTED BY THE SUPPLY - TO REVIEW BY PD FOCAL POINT', obj, 'danger')
        if obj and 'approved' in request.POST and not obj.approval_date:
            if obj.approved is True:
                obj.approval_date = datetime.datetime.now()
                obj.approved_by = request.user
                obj.status = obj.APPROVED
                DistributionPlan.objects.create(plan=obj)
                send_notification('UNICEF_PD', 'SUPPLY PLAN APPROVED BY THE BUDGET OWNER', obj)
                send_notification('PARTNER', 'DISTRIBUTION PLAN CREATED - PARTNER WILL BE NOTIFIED', obj, 'info', obj.partner_id)
            elif obj.approved is False:
                send_notification('SUPPLY_ADMIN', 'SUPPLY PLAN REJECTED BY THE BUDGET OWNER - TO REVIEW BY SUPPLY', obj, 'danger')
        super(SupplyPlanAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(SupplyPlanAdmin, self).get_queryset(request)
        if has_group(request.user, 'UNICEF_PD'):
            qs = qs.filter(created_by=request.user)
        if has_group(request.user, 'BUDGET_OWNER'):
            qs = qs.filter(status__in=['reviewed', 'approved'])
        return qs


class DistributionPlanItemInline(admin.StackedInline):
    model = DistributionPlanItem
    max_num = 99
    min_num = 0
    extra = 0
    verbose_name = 'Request per wave'
    verbose_name_plural = 'Requests per wave'
    form = DistributionPlanItemForm
    formset = DistributionPlanItemFormSet
    suit_classes = u'suit-tab suit-tab-request'

    fields = (
        'wave',
        'site',
        'target_population',
        'delivery_location',
        'contact_person',
        'quantity_requested',
        'date_required_by',
        'date_distributed_by',
    )

    def get_fields(self, request, obj=None):
        fields = [
            'wave',
            'site',
            'target_population',
            'delivery_location',
            'contact_person',
            'quantity_requested',
            'date_required_by',
            'date_distributed_by',
        ]

        if has_group(request.user, 'SUPPLY_FP'):
            fields.append('delivery_expected_date')
        return fields

    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.args:
            return self.parent_model.objects.get(pk=resolved.args[0])
        return None

    def has_add_permission(self, request):
        parent = self.get_parent_object_from_request(request)
        if parent and parent.submitted:
            return False
        return True

    # def has_change_permission(self, request, obj=None):
    #     parent = self.get_parent_object_from_request(request)
    #     if parent and parent.submitted:
    #         return False
    #     return True

    def has_delete_permission(self, request, obj=None):
        parent = self.get_parent_object_from_request(request)
        if parent and parent.submitted:
            return False
        return True


class ReceivedItemInline(admin.TabularInline):
    model = DistributionPlanItemReceived
    max_num = 0
    min_num = 0
    extra = 0
    verbose_name = 'Received item'
    verbose_name_plural = 'Received items'
    suit_classes = u'suit-tab suit-tab-receiving'

    fields = (
        'wave_number',
        'supply_item',
        'quantity_requested',
        'quantity_received',
        'date_received',
        'quantity_balance',
    )

    readonly_fields = (
        'wave_number',
        'supply_item',
        'quantity_requested',
        'quantity_balance',
    )

    def quantity_balance(self, obj):
        try:
            if obj and obj.quantity_received:
                return obj.quantity_requested - obj.quantity_received
        except Exception as ex:
            pass
        return 0

    def quantity_distributed_balance(self, obj):
        try:
            if obj.quantity_received and obj.quantity_distributed:
                return obj.quantity_received - obj.quantity_distributed
        except Exception:
            pass
        return 0


class DistributedItemSiteInline(nested_admin.NestedTabularInline):
    model = DistributedItemSite
    max_num = 99
    min_num = 0
    extra = 0
    verbose_name = 'Site'
    verbose_name_plural = 'Sites'
    fk_name = 'plan'
    suit_classes = u'suit-tab suit-tab-distribution'
    form = DistributedItemSiteForm
    formset = DistributedItemSiteFormSet

    fields = (
        'site',
        'quantity_distributed_per_site',
        'distribution_date',
        'tpm_visit',
    )

    def get_readonly_fields(self, request, obj=None):

        fields = [
           'tpm_visit',
        ]
        if (has_group(request.user, 'UNICEF_PO') or has_group(request.user, 'FIELD_FP')) \
            and obj and obj.plan.status == DistributionPlan.COMPLETED:
            fields.remove('tpm_visit')

        return fields


class DistributedItemInline(nested_admin.NestedStackedInline):
    model = DistributedItem
    max_num = 0
    min_num = 0
    extra = 0
    verbose_name = 'Distributed item per site'
    verbose_name_plural = 'Distributed items'
    fk_name = 'plan'
    suit_classes = u'suit-tab suit-tab-distribution'

    fields = (
        'wave_number',
        'supply_item',
        'quantity_requested',
    )
    readonly_fields = (
        'wave_number',
        'supply_item',
        'quantity_requested',
    )
    inlines = [DistributedItemSiteInline, ]


class DistributionPlanResource(resources.ModelResource):
    class Meta:
        model = DistributionPlan
        fields = (
            'plan',
        )
        export_order = fields


class DistributionPlanAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
    resource_class = DistributionPlanResource
    form = DistributionPlanForm
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'reference_number',
                'plan_partner',
                'plan_partnership',
                'plan_section',
                'status',
                'comments'
            ]
        }),
        ('Review by UNICEF field focal point', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'reviewed',
                'review_date',
                'reviewed_by',
                'review_comments',
            ]
        }),
        ('Clearness by UNICEF Supply Beirut focal point', {
            'classes': ('suit-tab', 'suit-tab-general',),
            'fields': [
                'cleared',
                'cleared_by',
                'cleared_date',
                'cleared_comments',
            ]
        }),
        ('Approval by UNICEF programme officer (PD focal point)', {
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
                      ('receiving', 'Received Items'),
                      ('distribution', 'Distributed Items'),
                    )

    search_fields = (
        'plan__partnership',
    )
    list_display = (
        'reference_number',
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

    inlines = [DistributionPlanItemInline, ReceivedItemInline, DistributedItemInline]

    def get_readonly_fields(self, request, obj=None):

        fields = [
            'reference_number',
            'plan',
            'plan_partner',
            'plan_partnership',
            'plan_section',
            'status',
            'reviewed',
            'review_date',
            'reviewed_by',
            'review_comments',
            'cleared',
            'cleared_by',
            'cleared_date',
            'cleared_comments',
            'approved',
            'approved_by',
            'approval_date',
            'approval_comments',
        ]

        if has_group(request.user, 'FIELD_FP') and obj:
            fields.remove('reviewed')
            fields.remove('review_comments')

        if has_group(request.user, 'SUPPLY_FP') and obj:
            fields.remove('cleared')
            fields.remove('cleared_comments')

        if has_group(request.user, 'UNICEF_PD') and obj:
            fields.remove('approved')
            fields.remove('approval_comments')

        if has_group(request.user, 'PARTNER'):
            fields.remove('status')

        return fields

    def get_form(self, request, obj=None, **kwargs):
        form = super(DistributionPlanAdmin, self).get_form(request, obj, **kwargs)
        form.request = request
        if has_group(request.user, 'PARTNER'):
            form.base_fields['status'].choices = (
                (DistributionPlan.PLANNED, u"Planned"),
                (DistributionPlan.SUBMITTED, u"Submitted/Plan completed"),
                (DistributionPlan.RECEIVED, u"All waves received"),
                (DistributionPlan.COMPLETED, u"Distribution Completed"),
            )

        return form

    def save_model(self, request, obj, form, change):
        send_notification('SUPPLY_ADMIN', 'DISTRIBUTION PLAN TEST', obj)
        if not change and obj and obj.status == obj.PLANNED:
            obj.created_by = request.user
        if obj and not obj.submitted and obj.status == obj.SUBMITTED:  # submitted by the partner
            obj.submission_date = datetime.datetime.now()
            obj.submitted_by = request.user
            obj.submitted = True
            obj.to_review = True
            send_notification('FIELD_FP', 'DISTRIBUTION PLAN SUBMITTED BY THE PARTNER - TO REVIEW BY THE FIELD FOCAL POINT', obj)
            send_notification('SUPPLY_ADMIN', 'DISTRIBUTION PLAN SUBMITTED BY THE PARTNER', obj)

        if obj and 'reviewed' in request.POST and not obj.review_date:  # by the field focal point
            if obj.reviewed is True:
                obj.review_date = datetime.datetime.now()
                obj.reviewed_by = request.user
                obj.status = obj.REVIEWED
                send_notification('PARTNER', 'DISTRIBUTION PLAN REVIEWED BY THE FIELD FOCAL POINT', obj)
                send_notification('SUPPLY_ADMIN', 'DISTRIBUTION PLAN REVIEWED BY FIELD FOCAL POINT - TO BE CLEARED BY SUPPLY', obj)
            elif obj.reviewed is False:
                obj.status = obj.PLANNED
                obj.submission_date = None
                obj.submitted = False
                send_notification('PARTNER', 'DISTRIBUTION PLAN REJECTED BY THE FIELD FOCAL POINT - TO BE REVIEWED BY THE PARTNER', obj, 'danger')

        if obj and 'cleared' in request.POST and not obj.cleared_date:  # cleared by the supply
            if obj.cleared is True:
                obj.cleared_date = datetime.datetime.now()
                obj.cleared_by = request.user
                obj.status = obj.CLEARED
                send_notification('FIELD_FP', 'DISTRIBUTION PLAN CLEARED BY SUPPLY', obj)
                send_notification('UNICEF_PD', 'DISTRIBUTION PLAN CLEARED BY SUPPLY - TO APPROVED BY THE PD FOCAL POINT', obj)
            elif obj.cleared is False:
                obj.reviewed = None
                obj.review_date = None
                obj.reviewed_by = None
                obj.status = obj.SUBMITTED
                send_notification('FIELD_FP', 'DISTRIBUTION PLAN REJECTED BY THE SUPPLY - TO REVIEW BY FIELD FOCAL POINT', obj, 'danger')

        if obj and 'approved' in request.POST and not obj.approval_date:  # approval by the PD focal point
            if obj.approved is True:
                obj.approval_date = datetime.datetime.now()
                obj.approved_by = request.user
                obj.status = obj.APPROVED
                send_notification('SUPPLY_ADMIN', 'DISTRIBUTION PLAN APPROVED BY THE PD FOCAL POINT', obj)
            elif obj.approved is False:
                obj.cleared = None
                obj.cleared_date = None
                obj.cleared_by = None
                obj.status = obj.REVIEWED
                send_notification('SUPPLY_ADMIN', 'DISTRIBUTION PLAN REJECTED BY THE PD FOCAL POINT - TO REVIEW BY SUPPLY', obj, 'danger')

        if obj and obj.status == obj.RECEIVED and not obj.item_received:  # by the partner
            obj.item_received = True
            obj.item_received_date = datetime.datetime.now()
            send_notification('SUPPLY_ADMIN', 'DISTRIBUTION PLAN - PARTNER RECEIVED ALL WAVES', obj)
        if obj and obj.status == obj.COMPLETED and not obj.item_distributed:  # by the partner
            obj.item_distributed = True
            obj.item_distributed_date = datetime.datetime.now()
            send_notification('SUPPLY_ADMIN', 'DISTRIBUTION PLAN - PARTNER DISTRIBUTED ALL ITEMS', obj)
        if change and obj.requests.all():  # by the supply
            items = obj.requests.all()
            for wave_item in items:
                if wave_item.delivery_expected_date:
                    item = wave_item.wave.supply_plan.item
                    DistributionPlanItemReceived.objects.get_or_create(
                        wave=wave_item,
                        wave_number=wave_item.wave.wave_number,
                        plan=obj,
                        supply_item=item,
                        quantity_requested=wave_item.quantity_requested
                    )
                    DistributedItem.objects.get_or_create(
                        wave=wave_item,
                        wave_number=wave_item.wave.wave_number,
                        plan=obj,
                        supply_item=item,
                        quantity_requested=wave_item.quantity_requested
                    )
                    send_notification('PARTNER', 'DISTRIBUTION PLAN - ITEMS WILL BE DELIVERED TO THE PARTNER', obj, 'warning', obj.plan.partner_id)
        super(DistributionPlanAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(DistributionPlanAdmin, self).get_queryset(request)
        if has_group(request.user, 'PARTNER'):
            return qs.filter(plan__partner_id=request.user.partner_id)
        # if has_group(request.user, 'FIELD_FP'):
        #     return qs.filter(status__in=['planned', 'reviewed', 'submitted', 'completed'])
        if has_group(request.user, 'UNICEF_PD'):
            return qs.filter(plan__section=request.user.section)
        return qs


admin.site.register(SupplyPlan, SupplyPlanAdmin)
admin.site.register(DistributionPlan, DistributionPlanAdmin)

