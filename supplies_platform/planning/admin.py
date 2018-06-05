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
    SupplyPlanWave,
    SupplyPlanWaveItem,
    DistributionPlan,
    DistributionPlanWave,
    DistributionPlanWaveItem,
    DistributionPlanItemReceived,
    DistributedItem,
    DistributedItemSite,
)
from .forms import (
    SupplyPlanForm,
    # SupplyPlanWaveForm,
    SupplyPlanWaveFormSet,
    DistributionPlanForm,
    DistributedItemSiteForm,
    DistributedItemSiteFormSet,
    DistributionPlanWaveForm,
    DistributionPlanWaveFormSet,
    DistributionPlanWaveItemForm,
    DistributionPlanItemReceivedFormSet,
)


class QuantityGapFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Quantity GAP'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'quantity_gap'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', 'Yes'),
            ('no', 'No')
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() and self.value() == 'yes':
            gaps = DistributionPlanItemReceived.objects.extra(where=[
                'date_received IS NOT NULL', 'quantity_requested != quantity_received'
            ]).values_list('plan_id', flat=True).distinct()
            return queryset.filter(pk__in=gaps)
        if self.value() and self.value() == 'no':
            gaps = DistributionPlanItemReceived.objects.extra(where=[
                'quantity_requested = quantity_received'
            ]).values_list('plan_id', flat=True)
            return queryset.filter(pk__in=gaps)
        return queryset


class LateDeliveryFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Late Delivery'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'late_delivery'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', 'Yes'),
            ('no', 'No')
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() and self.value() == 'yes':
            return queryset.filter(
                received__isnull=False,
                received__date_received__isnull=True,
                plan_waves__isnull=False,
                plan_waves__delivery_expected_date__isnull=False,
                plan_waves__delivery_expected_date__lt=datetime.datetime.now()
            ).distinct()
        if self.value() and self.value() == 'no':
            return queryset.filter(
                received__isnull=False,
                received__date_received__isnull=True,
                plan_waves__isnull=False,
                plan_waves__delivery_expected_date__isnull=False,
                plan_waves__delivery_expected_date__lt=datetime.datetime.now()
            ).distinct()
        return queryset


class UpcomingDeliveryFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Upcoming Delivery'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'upcoming_delivery'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', 'Yes'),
            ('no', 'No')
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() and self.value() == 'yes':
            return queryset.filter(
                received__isnull=False,
                received__date_received__isnull=True,
                plan_waves__isnull=False,
                plan_waves__delivery_expected_date__isnull=False,
                plan_waves__delivery_expected_date__gte=datetime.datetime.now(),
                plan_waves__delivery_expected_date__lte=datetime.datetime.now() + datetime.timedelta(days=15),
            ).distinct()
        if self.value() and self.value() == 'no':
            return queryset
        return queryset


class SupplyPlanWaveItemInline(nested_admin.NestedTabularInline):
    model = SupplyPlanWaveItem
    verbose_name = 'Item'
    verbose_name_plural = 'Items'
    extra = 0
    min_num = 0
    max_num = 0
    fk_name = 'plan_wave'
    suit_classes = u'suit-tab suit-tab-waves'

    fields = (
        'item',
        'quantity',
        'item_price',
        'total_budget',
        'beneficiaries_covered_per_item',
        # 'target_population',
    )

    readonly_fields = (
        'item',
        'item_price',
        'total_budget',
        # 'target_population',
        'beneficiaries_covered_per_item',
    )

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False


class SupplyPlanWaveInline(nested_admin.NestedStackedInline):
    model = SupplyPlanWave
    # form = WavePlanForm
    formset = SupplyPlanWaveFormSet
    verbose_name = 'Wave'
    verbose_name_plural = 'Waves'
    min_num = 0
    max_num = 0
    extra = 0
    fk_name = 'supply_plan'
    suit_classes = u'suit-tab suit-tab-waves'

    fields = (
        'date_required_by',
    )

    inlines = [SupplyPlanWaveItemInline, ]

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False


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
        ('Supply Items', {
            'classes': ('suit-tab', 'suit-tab-waves',),
            'fields': [
                'items',
                'wave_number',
            ]
        }),
    ]

    suit_form_tabs = (
                      ('general', 'Supply Plan'),
                      ('waves', 'Supply Items'),
                    )

    inlines = [SupplyPlanWaveInline, ]

    filter_horizontal = ('items',)

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
        if obj and obj.id and obj.status == obj.PLANNED and not obj.supply_plans_waves.all().count() and obj.wave_number and obj.items.all().count():
            for x in range(1, obj.wave_number+1):
                plan_wave, created = SupplyPlanWave.objects.get_or_create(
                    supply_plan=obj,
                    wave_number=x
                )
                plan_wave.save()
                for item in obj.items.all():
                    SupplyPlanWaveItem.objects.get_or_create(
                        plan=obj,
                        plan_wave=plan_wave,
                        item=item,
                        quantity=0
                    )
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
                dist_plan, created = DistributionPlan.objects.get_or_create(plan=obj)
                for plan_wave in obj.supply_plans_waves.all():
                    dist_plan_wave = DistributionPlanWave.objects.create(
                        plan=dist_plan,
                        wave_number=plan_wave.wave_number,
                        wave=plan_wave,
                    )
                    for wave_item in plan_wave.supply_plan_wave_items.all():
                        DistributionPlanWaveItem.objects.create(
                            plan_wave=dist_plan_wave,
                            wave_item=wave_item,
                            item=wave_item.item,
                            quantity_requested=wave_item.quantity
                        )

                send_notification('UNICEF_PD', 'SUPPLY PLAN APPROVED BY THE BUDGET OWNER', obj)
                send_notification('PARTNER', 'DISTRIBUTION PLAN CREATED - PARTNER WILL BE NOTIFIED', dist_plan, '#request', 'info', obj.partner_id)
            elif obj.approved is False:
                obj.review_date = None
                obj.reviewed_by = None
                obj.status = obj.SUBMITTED
                send_notification('SUPPLY_ADMIN', 'SUPPLY PLAN REJECTED BY THE BUDGET OWNER - TO REVIEW BY SUPPLY', obj, '#general', 'danger')
        super(SupplyPlanAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(SupplyPlanAdmin, self).get_queryset(request)
        if has_group(request.user, 'UNICEF_PD'):
            qs = qs.filter(created_by=request.user)
        if has_group(request.user, 'BUDGET_OWNER'):
            qs = qs.filter(status__in=['reviewed', 'approved'])
        return qs


class ReceivedItemInline(admin.TabularInline):
    model = DistributionPlanItemReceived
    formset = DistributionPlanItemReceivedFormSet
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
        'unicef_visit',
    )

    def get_readonly_fields(self, request, obj=None):

        fields = [
           'tpm_visit',
           'unicef_visit',
        ]
        if obj and (has_group(request.user, 'UNICEF_PO') or has_group(request.user, 'FIELD_FP')):
            fields.remove('tpm_visit')
            fields.remove('unicef_visit')

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


class DistributionPlanWaveItemInline(nested_admin.NestedTabularInline):
    model = DistributionPlanWaveItem
    form = DistributionPlanWaveItemForm
    verbose_name = 'Item'
    verbose_name_plural = 'Items'
    extra = 0
    min_num = 0
    max_num = 0
    fk_name = 'plan_wave'
    suit_classes = u'suit-tab suit-tab-request'

    fields = (
        'item',
        'quantity_requested',
        'target_population',
        'date_distributed_by',
    )

    readonly_fields = (
        'item',
        'quantity_requested',
    )

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False


class DistributionPlanWaveInline(nested_admin.NestedStackedInline):
    model = DistributionPlanWave
    form = DistributionPlanWaveForm
    formset = DistributionPlanWaveFormSet
    verbose_name = 'Wave'
    verbose_name_plural = 'Waves'
    min_num = 0
    max_num = 0
    extra = 0
    fk_name = 'plan'
    suit_classes = u'suit-tab suit-tab-request'

    fields = (
        'site',
        'delivery_site',
        'date_required_by',
        'contact_person',
    )

    inlines = [DistributionPlanWaveItemInline, ]

    def get_fields(self, request, obj=None):
        fields = [
            'site',
            'delivery_site',
            'date_required_by',
            'contact_person',
        ]

        if has_group(request.user, 'SUPPLY_FP'):
            fields.append('delivery_expected_date')
        return fields

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False


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
        ('Plan Overview', {
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
        QuantityGapFilter,
        LateDeliveryFilter,
        UpcomingDeliveryFilter,
    )

    inlines = [DistributionPlanWaveInline, ReceivedItemInline, DistributedItemInline]

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

        if has_group(request.user, 'FIELD_FP') and obj and obj.status == obj.SUBMITTED:
            fields.remove('reviewed')
            fields.remove('review_comments')

        if has_group(request.user, 'SUPPLY_FP') and obj and obj.status == obj.REVIEWED:
            fields.remove('cleared')
            fields.remove('cleared_comments')

        if has_group(request.user, 'UNICEF_PD') and obj and obj.status == obj.CLEARED:
            fields.remove('approved')
            fields.remove('approval_comments')

        if has_group(request.user, 'PARTNER'):
            fields.remove('status')

        return fields

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(DistributionPlanAdmin, self).get_form(request, obj, **kwargs)
    #     form.request = request
    #     if has_group(request.user, 'PARTNER'):
    #         form.base_fields['status'].choices = (
    #             (DistributionPlan.PLANNED, u"Planned"),
    #             (DistributionPlan.SUBMITTED, u"Submitted/Plan completed"),
    #             (DistributionPlan.RECEIVED, u"All waves received"),
    #             (DistributionPlan.COMPLETED, u"Distribution Completed"),
    #         )
    #
    #     return form

    def save_model(self, request, obj, form, change):
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

        # if obj and obj.status == obj.RECEIVED and not obj.item_received:  # by the partner
        #     obj.item_received = True
        #     obj.item_received_date = datetime.datetime.now()
        #     send_notification('SUPPLY_ADMIN', 'DISTRIBUTION PLAN - PARTNER RECEIVED ALL WAVES', obj)
        # if obj and obj.status == obj.COMPLETED and not obj.item_distributed:  # by the partner
        #     obj.item_distributed = True
        #     obj.item_distributed_date = datetime.datetime.now()
        #     send_notification('SUPPLY_ADMIN', 'DISTRIBUTION PLAN - PARTNER DISTRIBUTED ALL ITEMS', obj)
        if change and obj.plan_waves.all():  # by the supply
            for plan_wave in obj.plan_waves.all():
                if plan_wave.delivery_expected_date:
                    for wave_item in plan_wave.plan_wave_items.all():
                        DistributionPlanItemReceived.objects.get_or_create(
                            plan=obj,
                            wave_plan=plan_wave,
                            wave_item=wave_item,
                            supply_item=wave_item.item,
                            wave_number=plan_wave.wave_number,
                            quantity_requested=wave_item.quantity_requested,
                        )
                        dist_item, create = DistributedItem.objects.get_or_create(
                            plan=obj,
                            wave_plan=plan_wave,
                            wave_item=wave_item,
                            supply_item=wave_item.item,
                            wave_number=plan_wave.wave_number,
                            quantity_requested=wave_item.quantity_requested,
                        )
                        DistributedItemSite.objects.get_or_create(
                            plan=dist_item,
                            site=plan_wave.site
                        )
                    send_notification('PARTNER', 'DISTRIBUTION PLAN - ITEMS WILL BE DELIVERED TO THE PARTNER', obj, '#request', 'warning', obj.plan.partner_id)
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

