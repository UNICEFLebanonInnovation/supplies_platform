
from django.utils.translation import ugettext as _
from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import messages
from dal import autocomplete

from django.core.exceptions import (
    ValidationError,
    ObjectDoesNotExist,
    MultipleObjectsReturned
)

from supplies_platform.partners.models import PartnerStaffMember
from supplies_platform.locations.models import Location
from supplies_platform.supplies.models import SupplyItem
from .models import (
    SupplyPlan,
    SupplyPlanItem,
    WavePlan,
    DistributionPlan,
    DistributionPlanItem,
    WavePlan,
    DistributionPlanWave
)


class WavePlanForm(forms.ModelForm):

    class Meta:
        model = WavePlan
        fields = '__all__'


class WavePlanFormSet(BaseInlineFormSet):

    def clean(self):
        """
        Ensure distribution plans are inline with overall supply plan
        """
        cleaned_data = super(WavePlanFormSet, self).clean()

        if self.instance:
            for plan in self.instance.supply_plans_waves.all():
                total_quantity = 0
                for form in self.forms:
                    if form.cleaned_data.get('DELETE', False):
                        continue
                    data = form.cleaned_data
                    # if plan.item == data.get('item', 0):
                    total_quantity += data.get('quantity_required', 0)

                if total_quantity > self.instance.quantity:
                    raise ValidationError(
                        _(u'The total quantity ({}) of {} exceeds the planned amount of {}'.format(
                            total_quantity, self.instance.item, self.instance.quantity))
                    )

        return cleaned_data


class DistributionPlanForm(forms.ModelForm):

    class Meta:
        model = DistributionPlan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Only show supply items already in the supply plan
        """
        if 'parent_object' in kwargs:
            self.parent_partnership = kwargs.pop('parent_object')

        super(DistributionPlanForm, self).__init__(*args, **kwargs)

        queryset = SupplyItem.objects.none()
        if hasattr(self, 'parent_partnership'):

            items = self.parent_partnership.supply_plans.all().values_list('item__id', flat=True)
            queryset = SupplyItem.objects.filter(id__in=items)

        self.fields['item'].queryset = queryset


class DistributionPlanFormSet(BaseInlineFormSet):

    def clean(self):
        """
        Ensure distribution plans are inline with overall supply plan
        """
        cleaned_data = super(DistributionPlanFormSet, self).clean()

        if self.instance:
            for plan in self.instance.supply_plans.all():
                total_quantity = 0
                for form in self.forms:
                    if form.cleaned_data.get('DELETE', False):
                        continue
                    data = form.cleaned_data
                    if plan.item == data.get('item', 0):
                        total_quantity += data.get('quantity', 0)

                if total_quantity > plan.quantity:
                    raise ValidationError(
                        _(u'The total quantity ({}) of {} exceeds the planned amount of {}'.format(
                            total_quantity, plan.item, plan.quantity))
                    )

        return cleaned_data


class DistributionPlanItemForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=autocomplete.ModelSelect2(url='location_autocomplete')
    )
    delivery_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=autocomplete.ModelSelect2(url='location_autocomplete')
    )

    class Meta:
        model = DistributionPlanItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Only show supply items already in the supply plan
        """
        if 'parent_object' in kwargs:
            self.parent_object = kwargs.pop('parent_object')

        super(DistributionPlanItemForm, self).__init__(*args, **kwargs)

        queryset = WavePlan.objects.none()
        queryset1 = PartnerStaffMember.objects.none()
        if hasattr(self, 'parent_object'):
            queryset = WavePlan.objects.filter(supply_plan__supply_plan_id=self.parent_object.plan_id)
            queryset1 = PartnerStaffMember.objects.filter(partner_id=self.parent_object.plan.partner_id)

        self.fields['wave'].queryset = queryset
        self.fields['contact_person'].queryset = queryset1


class DistributionPlanItemFormSet(BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super(DistributionPlanItemFormSet, self).get_form_kwargs(index)
        kwargs['parent_object'] = self.instance
        return kwargs


class DistributionPlanWaveForm(forms.ModelForm):

    # delivery_location = forms.ModelChoiceField(
    #     queryset=Location.objects.all(),
    #     widget=autocomplete.ModelSelect2(url='location_autocomplete')
    # )

    class Meta:
        model = DistributionPlanWave
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     """
    #     Only show supply items already in the supply plan
    #     """
    #     if 'parent_object' in kwargs:
    #         self.parent_object = kwargs.pop('parent_object')
    #
    #     super(DistributionPlanWaveForm, self).__init__(*args, **kwargs)
    #
    #     queryset = SupplyItem.objects.all()
    #     if hasattr(self, 'parent_object'):
    #         queryset = SupplyPlanItem.objects.filter(supply_plan_id=self.parent_object.plan.plan_id)
    #
    #     self.fields['supply_item'].queryset = queryset


class DistributionPlanWaveFormSet(BaseInlineFormSet):

    def get_form_kwargs(self, index):
        kwargs = super(DistributionPlanWaveFormSet, self).get_form_kwargs(index)
        kwargs['parent_object'] = self.instance
        return kwargs

    # def clean(self):
    #     """
    #     Ensure distribution plans are inline with overall supply plan
    #     """
    #     cleaned_data = super(DistributionPlanWaveFormSet, self).clean()
    #
    #     if self.instance:
    #         print(self.insatance.plan_id)
    #         for plan in self.instance.supply_plans_waves.all():
    #             total_quantity = 0
    #             for form in self.forms:
    #                 if form.cleaned_data.get('DELETE', False):
    #                     continue
    #                 data = form.cleaned_data
    #                 # if plan.item == data.get('item', 0):
    #                 total_quantity += data.get('quantity_required', 0)
    #
    #             print(total_quantity)
    #
    #             if total_quantity > self.instance.quantity:
    #                 raise ValidationError(
    #                     _(u'The total quantity ({}) of {} exceeds the planned amount of {}'.format(
    #                         total_quantity, self.instance.item, self.instance.quantity))
    #                 )
    #
    #     return cleaned_data
