from __future__ import unicode_literals

from django.apps import AppConfig


class DriversConfig(AppConfig):
    name = 'supplies_platform.drivers'
    verbose_name = "Drivers"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass

