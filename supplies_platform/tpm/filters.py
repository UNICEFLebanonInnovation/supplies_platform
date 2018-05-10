from django.utils.translation import ugettext as _

from django_filters import FilterSet, ModelChoiceFilter

from .models import TPMVisit


class TPMVisitFilter(FilterSet):

    class Meta:
        model = TPMVisit
        fields = {

        }
