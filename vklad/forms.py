from django import forms
from .models import VkladInvestHistory
# from urllib import request
# from django.core.files.base import ContentFile
# from django.utils.text import slugify
# Create your forms here.


class FormVkladInvestHistory(forms.ModelForm):
    cash = forms.DecimalField(max_digits=10, decimal_places=2)
    date = forms.DateField()
    popolnenie = forms.BooleanField(required=False)

    class Meta:
        model = VkladInvestHistory
        exclude = ['vklad']
