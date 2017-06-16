from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, UserType
from django.utils.translation import ugettext_lazy as _




class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])



@admin.register(User)
class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    AuthUserAdmin.fieldsets[1][1]["fields"] += ("phone_number",)

    fieldsets = (('User Profile', {'fields': ('name','usr_type')}),
                ) + AuthUserAdmin.fieldsets

    list_display = ('username', 'name','usr_type','is_superuser')
    search_fields = ['name']


#admin.site.register(User)
admin.site.register(UserType)
