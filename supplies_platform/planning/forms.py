
from django.utils.translation import ugettext as _
from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import messages
from datetime import date
from dal import autocomplete

from django.core.exceptions import (
    ValidationError,
    ObjectDoesNotExist,
    MultipleObjectsReturned
)

from supplies_platform.backends.utils import send_notification

from supplies_platform.partners.models import PartnerStaffMember
from supplies_platform.locations.models import Location
from supplies_platform.supplies.models import SupplyItem
from supplies_platform.tpm.models import TPMVisit
from supplies_platform.users.models import User
from .models import (
    SupplyPlan,
    DistributionPlan,
    DistributionPlanItem,
    WavePlan,
    DistributedItem,
    DistributedItemSite,
    DistributionPlanItemReceived,
    DistributionPlanWave,
    DistributionPlanWaveItem
)

YES_NO_CHOICE = (
    (True, 'Yes'),
    (False, 'No')
)


class SupplyPlanForm(forms.ModelForm):

    tpm_focal_point = forms.ModelChoiceField(
        required=False, label='TPM focal point',
        queryset=User.objects.filter(groups__name='TPM_COMPANY')
    )

    reviewed = forms.ChoiceField(widget=forms.RadioSelect, choices=YES_NO_CHOICE, initial=False)
    approved = forms.ChoiceField(widget=forms.RadioSelect, choices=YES_NO_CHOICE, initial=False)

    class Meta:
        model = SupplyPlan
        fields = '__all__'

    def clean(self):
        """
        Ensure distribution plans are inline with overall supply plan
        """
        cleaned_data = super(SupplyPlanForm, self).clean()
        if cleaned_data.get('DELETE', False):
            return cleaned_data

        pca = cleaned_data.get('pca', 0)
        if pca:
            current_date = date.today()
            if current_date > pca.end:
                raise ValidationError(
                    _(u'Please select a valid partnership')
                )

        return cleaned_data


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

        if self.instance and hasattr(self.instance, 'supply_plan'):
            pca = self.instance.supply_plan.pca

            for plan in self.instance.supply_plans_waves.all():
                total_quantity = 0
                for form in self.forms:
                    if form.cleaned_data.get('DELETE', False):
                        continue
                    data = form.cleaned_data
                    # if plan.item == data.get('item', 0):
                    date_required_by = data.get('date_required_by', 0)

                    if pca and date_required_by > pca.end:
                        raise ValidationError(
                            _(u'The required date ({}) should be between {} and {}'.format(
                                date_required_by, pca.start, pca.end))
                        )

                    total_quantity += data.get('quantity_required', 0)

                if total_quantity > self.instance.quantity:
                    raise ValidationError(
                        _(u'The total quantity ({}) of {} exceeds the planned amount of {}'.format(
                            total_quantity, self.instance.item, self.instance.quantity))
                    )

        return cleaned_data


class DistributionPlanForm(forms.ModelForm):

    reviewed = forms.ChoiceField(widget=forms.RadioSelect, choices=YES_NO_CHOICE, initial=False)
    cleared = forms.ChoiceField(widget=forms.RadioSelect, choices=YES_NO_CHOICE, initial=False)
    approved = forms.ChoiceField(widget=forms.RadioSelect, choices=YES_NO_CHOICE, initial=False)

    class Meta:
        model = DistributionPlan
        fields = '__all__'


class DistributionPlanItemForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=autocomplete.ModelSelect2(url='location_autocomplete')
    )
    delivery_location = forms.ModelChoiceField(
        required=False,
        queryset=Location.objects.all(),
        help_text=u'Leave it empty if the same save the Site above',
        widget=autocomplete.ModelSelect2(url='location_autocomplete')
    )
    contact_person = forms.ModelChoiceField(
        required=False,
        queryset=PartnerStaffMember.objects.all()
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

        if hasattr(self, 'parent_object') and not self.parent_object.submitted:
            self.fields['wave'].queryset = queryset
            self.fields['contact_person'].queryset = queryset1

            if queryset1.count() == 1:
                self.fields['contact_person'].initial = queryset1.first


class DistributionPlanItemFormSet(BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super(DistributionPlanItemFormSet, self).get_form_kwargs(index)
        kwargs['parent_object'] = self.instance
        return kwargs

    def clean(self):
        """
        Ensure distribution plans are inline with overall supply plan
        """
        cleaned_data = super(DistributionPlanItemFormSet, self).clean()

        if self.instance and self.instance.plan and self.instance.plan.pca:
            partnership_start_date = self.instance.plan.pca.start
            partnership_end_date = self.instance.plan.pca.end
            for form in self.forms:
                if form.cleaned_data.get('DELETE', False):
                    continue
                data = form.cleaned_data
                date_required_by = data.get('date_required_by', 0)
                wave = data.get('wave', 0)
                wave_quantity_required = wave.quantity_required
                wave_date_required_by = wave.date_required_by
                quantity_requested = data.get('quantity_requested', 0)

                if quantity_requested > wave_quantity_required:
                    raise ValidationError(
                        _(u'The total quantity ({}) of {} exceeds the planned amount of {}'.format(
                            quantity_requested, wave.supply_plan.item.code, wave_quantity_required))
                    )

                if date_required_by < wave_date_required_by:
                    raise ValidationError(
                        _(u'The required date ({}) should be after {}'.format(
                            date_required_by, wave_date_required_by))
                    )

                if date_required_by > partnership_end_date:
                    raise ValidationError(
                        _(u'The required date ({}) should be between {} and {}'.format(
                            date_required_by, partnership_start_date, partnership_end_date))
                    )

        return cleaned_data


class DistributionPlanWaveForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=autocomplete.ModelSelect2(url='location_autocomplete')
    )
    delivery_site = forms.ModelChoiceField(
        required=False,
        queryset=Location.objects.all(),
        help_text=u'Leave it empty if the same save the Site above',
        widget=autocomplete.ModelSelect2(url='location_autocomplete')
    )
    contact_person = forms.ModelChoiceField(
        required=False,
        queryset=PartnerStaffMember.objects.all()
    )

    class Meta:
        model = DistributionPlanWave
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Only show supply items already in the supply plan
        """
        if 'parent_object' in kwargs:
            self.parent_object = kwargs.pop('parent_object')

        super(DistributionPlanWaveForm, self).__init__(*args, **kwargs)

        queryset1 = PartnerStaffMember.objects.none()
        if hasattr(self, 'parent_object'):
            queryset1 = PartnerStaffMember.objects.filter(partner_id=self.parent_object.plan.partner_id)

        if hasattr(self, 'parent_object') and not self.parent_object.submitted:
            self.fields['contact_person'].queryset = queryset1

            if queryset1.count() == 1:
                self.fields['contact_person'].initial = queryset1.first


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
    #     if self.instance and self.instance.plan and self.instance.plan.pca:
    #         partnership_start_date = self.instance.plan.pca.start
    #         partnership_end_date = self.instance.plan.pca.end
    #         for form in self.forms:
    #             if form.cleaned_data.get('DELETE', False):
    #                 continue
    #             data = form.cleaned_data
    #             date_required_by = data.get('date_required_by', 0)
    #             wave = data.get('wave', 0)
    #             wave_quantity_required = wave.quantity_required
    #             wave_date_required_by = wave.date_required_by
    #             quantity_requested = data.get('quantity_requested', 0)
    #
    #             if quantity_requested > wave_quantity_required:
    #                 raise ValidationError(
    #                     _(u'The total quantity ({}) of {} exceeds the planned amount of {}'.format(
    #                         quantity_requested, wave.supply_plan.item.code, wave_quantity_required))
    #                 )
    #
    #             if date_required_by < wave_date_required_by:
    #                 raise ValidationError(
    #                     _(u'The required date ({}) should be after {}'.format(
    #                         date_required_by, wave_date_required_by))
    #                 )
    #
    #             if date_required_by > partnership_end_date:
    #                 raise ValidationError(
    #                     _(u'The required date ({}) should be between {} and {}'.format(
    #                         date_required_by, partnership_start_date, partnership_end_date))
    #                 )
    #
    #     return cleaned_data


class DistributionItemFormSet(BaseInlineFormSet):

    def get_form_kwargs(self, index):
        kwargs = super(DistributionItemFormSet, self).get_form_kwargs(index)
        kwargs['parent_object'] = self.instance
        return kwargs


class DistributionItemForm(forms.ModelForm):

    class Meta:
        model = DistributedItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Only show supply items already in the supply plan
        """
        if 'parent_object' in kwargs:
            self.parent_object = kwargs.pop('parent_object')

        super(DistributionItemForm, self).__init__(*args, **kwargs)

        queryset = SupplyItem.objects.none()
        if hasattr(self, 'parent_object'):
            queryset = SupplyItem.objects.filter(id__in=[i.item_id for i in self.parent_object.plan.supply_plans.all()])

        self.fields['supply_item'].queryset = queryset


class DistributedItemSiteFormSet(BaseInlineFormSet):
    def save_existing_objects(self, commit=True):
        saved_instances = super(DistributedItemSiteFormSet, self).save_existing_objects(commit)
        if commit:
            for obj in saved_instances:
                if obj.tpm_visit:
                    plan = obj.plan.plan
                    instance, created = TPMVisit.objects.get_or_create(
                        distribution_plan=plan,
                        supply_plan=plan.plan,
                        supply_item=obj.plan.supply_item,
                        site=obj.site
                    )
                    if created:
                        instance.quantity_distributed = obj.quantity_distributed_per_site
                        instance.distribution_date = obj.distribution_date
                        instance.assigned_to_tpm = plan.plan.tpm_focal_point
                        instance.save()
                        send_notification('TPM_COMPANY', 'A NEW QUANTITATIVE SM VISIT HAS BEEN CREATED', instance)
                        send_notification('UNICEF_PO', 'A NEW QUALITATIVE SM VISIT HAS BEEN CREATED', instance)
        return saved_instances


class DistributedItemSiteForm(forms.ModelForm):

    site = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=autocomplete.ModelSelect2(url='location_autocomplete')
    )

    class Meta:
        model = DistributedItemSite
        fields = '__all__'

