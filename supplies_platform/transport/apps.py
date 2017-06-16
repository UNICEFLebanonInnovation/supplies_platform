from __future__ import unicode_literals

from django.apps import AppConfig


class TransportConfig(AppConfig):
    name = 'supplies_platform.transport'
    verbose_name = "Transport"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
