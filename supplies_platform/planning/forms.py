
import datetime

from django.utils.translation import ugettext as _
from django import forms
from django.forms.models import BaseInlineFormSet
# from datetimewidget.widgets import DateTimeWidget
# from bootstrap3_datetime.widgets import DateTimePicker
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
from supplies_platform.tpm.models import SMVisit
from supplies_platform.users.models import User
from .models import (
    SupplyPlan,
    SupplyPlanWave,
    DistributionPlan,
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


class SupplyPlanWaveFormSet(BaseInlineFormSet):

    def clean(self):
        """
        Ensure distribution plans are inline with overall supply plan
        """
        cleaned_data = super(SupplyPlanWaveFormSet, self).clean()

        if self.instance:

            for form in self.forms:
                if form.cleaned_data.get('DELETE', False):
                    continue
                data = form.cleaned_data
                date_required_by = data.get('date_required_by', 0)
                current_date = date.today()

                if date_required_by and date_required_by <= current_date:
                    raise ValidationError(
                        _(u"The required date ({}) should be after the current date".format(
                            date_required_by))
                    )

                if self.instance.pca and date_required_by > self.instance.pca.end:
                    pca = self.instance
                    raise ValidationError(
                        _(u'The required date ({}) should be between {} and {}'.format(
                            date_required_by, pca.start, pca.end))
                    )

        return cleaned_data


class DistributionPlanForm(forms.ModelForm):

    reviewed = forms.ChoiceField(widget=forms.RadioSelect, choices=YES_NO_CHOICE, initial=False)
    cleared = forms.ChoiceField(widget=forms.RadioSelect, choices=YES_NO_CHOICE, initial=False)
    approved = forms.ChoiceField(widget=forms.RadioSelect, choices=YES_NO_CHOICE, initial=False)

    class Meta:
        model = DistributionPlan
        fields = '__all__'


class DistributionPlanWaveForm(forms.ModelForm):
    site = forms.ModelChoiceField(
        required=False,
        queryset=Location.objects.all(),
        label=u'Distribution site',
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

    def clean(self):
        """
        Ensure distribution plans are inline with overall supply plan
        """
        cleaned_data = super(DistributionPlanWaveFormSet, self).clean()
        if self.instance and self.instance.plan:
            if self.instance.plan.pca:
                partnership_start_date = self.instance.plan.pca.start
                partnership_end_date = self.instance.plan.pca.end
            for form in self.forms:
                data = form.cleaned_data
                if form.cleaned_data.get('DELETE', False) or not data.get('date_required_by', 0):
                    continue
                instance = form.instance

                date_required_by = data.get('date_required_by', 0)

                if date_required_by < instance.wave.date_required_by:
                    raise ValidationError(
                        _(u'The required date ({}) should be grater than {}'.format(
                            date_required_by, instance.wave.date_required_by))
                    )

                if self.instance.plan.pca and date_required_by > partnership_end_date:
                    raise ValidationError(
                        _(u'The required date ({}) should be between {} and {}'.format(
                            date_required_by, partnership_start_date, partnership_end_date))
                    )

        return cleaned_data


class DistributionPlanWaveItemForm(forms.ModelForm):
    # date_distributed_by= forms.DateField()

    class Meta:
        model = DistributionPlanWaveItem
        fields = '__all__'


class DistributionPlanItemReceivedFormSet(BaseInlineFormSet):
    # def get_form_kwargs(self, index):
    #     kwargs = super(DistributionPlanItemReceivedFormSet, self).get_form_kwargs(index)
    #     kwargs['parent_object'] = self.instance
    #     return kwargs

    def clean(self):
        """
        Ensure distribution plans are inline with overall supply plan
        """
        cleaned_data = super(DistributionPlanItemReceivedFormSet, self).clean()
        if self.instance and self.instance.plan:
            for form in self.forms:
                data = form.cleaned_data
                if form.cleaned_data.get('DELETE', False):
                    continue

                instance = form.instance

                quantity_received = data.get('quantity_received', 0)
                date_received = data.get('date_received', 0)

                if quantity_received > 0 and not date_received:
                    raise ValidationError(
                        _(u'Please fill the received date for the quantity received ({})'.format(
                            quantity_received))
                    )
                if date_received and not quantity_received:
                    raise ValidationError(
                        _(u'Please fill the quantity received for the date received ({})'.format(
                            date_received))
                    )
                if date_received and instance.wave_item and date_received <= instance.wave_item.date_distributed_by:
                    raise ValidationError(
                        _(u"The received date ({}) should be after the planned distribution date ({})".format(
                            date_received, instance.wave_item.date_distributed_by))
                    )

        return cleaned_data


class DistributedItemSiteFormSet(BaseInlineFormSet):
    def save_existing_objects(self, commit=True):
        saved_instances = super(DistributedItemSiteFormSet, self).save_existing_objects(commit)
        if commit:
            for obj in saved_instances:
                if obj.tpm_visit:
                    plan = obj.plan.plan
                    instance, created = SMVisit.objects.get_or_create(
                        distribution_plan=plan,
                        supply_plan=plan.plan,
                        supply_item=obj.plan.supply_item,
                        site=obj.site,
                        type='quantity'
                    )
                    if created:
                        instance.quantity_distributed = obj.quantity_distributed_per_site
                        instance.distribution_date = obj.distribution_date
                        instance.assigned_to = plan.plan.tpm_focal_point
                        instance.save()
                        send_notification('TPM_COMPANY', 'A NEW QUANTITATIVE SM VISIT HAS BEEN CREATED', instance)
                if obj.unicef_visit:
                    plan = obj.plan.plan
                    instance, created = SMVisit.objects.get_or_create(
                        distribution_plan=plan,
                        supply_plan=plan.plan,
                        supply_item=obj.plan.supply_item,
                        site=obj.site,
                        type='quality',
                    )
                    if created:
                        instance.quantity_distributed = obj.quantity_distributed_per_site
                        instance.distribution_date = obj.distribution_date
                        instance.save()
                        send_notification('UNICEF_PO', 'A NEW QUALITATIVE SM VISIT HAS BEEN CREATED', instance)
        return saved_instances

    def clean(self):
        """
        Ensure distribution plans are inline with overall supply plan
        """
        cleaned_data = super(DistributedItemSiteFormSet, self).clean()
        if self.instance and self.instance.plan:
            for form in self.forms:
                data = form.cleaned_data
                if form.cleaned_data.get('DELETE', False):
                    continue

                instance = form.instance

                distribution_date = data.get('distribution_date', 0)

                # if quantity_received > 0 and not date_received:
                #     raise ValidationError(
                #         _(u'Please fill the received date for the quantity received ({})'.format(
                #             quantity_received))
                #     )

                # if distribution_date and distribution_date <= instance.wave_item.date_distributed_by:
                #     raise ValidationError(
                #         _(u"The distribution date ({}) should be after the received date ({})".format(
                #             distribution_date, instance.wave_item.date_distributed_by))
                #     )

        return cleaned_data


class DistributedItemSiteForm(forms.ModelForm):

    site = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=autocomplete.ModelSelect2(url='location_autocomplete')
    )

    class Meta:
        model = DistributedItemSite
        fields = '__all__'

