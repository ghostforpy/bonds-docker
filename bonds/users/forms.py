from django.contrib.auth import forms, get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from allauth.account import forms as allauth_forms
from django import forms as django_forms
User = get_user_model()


class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(forms.UserCreationForm):

    error_message = forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(forms.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])


class CustomSignUpForm(allauth_forms.SignupForm):
    privacy_politic_accept = django_forms.BooleanField(
        label='С политикой конфиденциальности согласен')

    def __init__(self, *args, **kwargs):
        super(CustomSignUpForm, self).__init__(*args, **kwargs)
        self.field_order = ['email', 'username', 'password', 'password2', 'privacy_politic_accept']

    def save(self, *args, **kwargs):
        user = super(CustomSignUpForm, self).save(*args, **kwargs)
        user.accept_private_policy = True
        user.save()
        return user
