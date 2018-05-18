from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from supplies_platform.partners.models import PartnerOrganization


class Section(models.Model):
    name = models.CharField(max_length=256)
    code = models.CharField(max_length=10, null=True, blank=True)
    color = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
# class UserType(models.Model):
#
#     type = models.CharField(max_length=254L)
#
#     def __str__(self):
#         return self.type
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    phone_number = models.CharField(
        _('Phone number'),
        max_length=20,
        null=True,
        blank=True
    )


    #usr_type = models.ForeignKey(UserType,blank=True ,null=True, verbose_name='User Type')
    section = models.ForeignKey(
        Section,
        null=True, blank=True
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        null=True, blank=True
    )

    def __str__(self):
        return '{} {}'.format(
            self.first_name,
            self.last_name
        )

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

