from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import EmailInput
from crispy_forms.layout import Layout, Field, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions


class BSAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=EmailInput(attrs={
            'placeholder': 'Email Address',
            'class': 'form-control',
            'title': 'Email',
        }),
        label=_("Email"),
        max_length=254,
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password',
                   'class': 'form-control',
                   'title': 'Password',
                   }),
        label=_("Password"),
    )
# BSAuthenticationForm
