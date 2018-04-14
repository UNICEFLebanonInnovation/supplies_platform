from django.shortcuts import render
from django.db.models import Q

from dal import autocomplete
from .models import Location


class LocationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Location.objects.none()

        qs = Location.objects.all()

        if self.q:
            qs = Location.objects.filter(
                Q(name__istartswith=self.q) | Q(p_code__istartswith=self.q)
            )

        return qs
