from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter

from .models import SMVisit


class SMVisitFilter(FilterSet):

    class Meta:
        model = SMVisit
        fields = {

        }
