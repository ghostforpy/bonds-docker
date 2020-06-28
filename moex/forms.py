from django import forms
from .models import TradeHistory


class SearchForm(forms.Form):
    query = forms.CharField()


class TradeHistoryForm(forms.ModelForm):
    class Meta:
        model = TradeHistory
        exclude = ['owner', 'security', 'buy']

    def clean(self):
        cleaned_data = super().clean()
        count = cleaned_data.get("count")
        price = cleaned_data.get("price")
        commission = cleaned_data.get("commission")
        if 'count' in cleaned_data and count <= 0:
            self.add_error('count', 'Count must be more then zero')
        if 'price' in cleaned_data and price <= 0:
            self.add_error('price', 'Price must be more then zero')
        if 'commission' in cleaned_data and commission < 0:
            self.add_error('commission',
                           'Commission must be more or equal then zero')
