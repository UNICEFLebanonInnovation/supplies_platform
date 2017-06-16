from __future__ import unicode_literals

from django.apps import AppConfig


class LocationsConfig(AppConfig):
    name = 'supplies_platform.locations'
    verbose_name = "Locations"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass

