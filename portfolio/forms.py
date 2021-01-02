from django import forms
from .models import InvestmentPortfolio, PortfolioInvestHistory


class PortfolioCreateForm(forms.ModelForm):
    class Meta:
        model = InvestmentPortfolio
        fields = ('title', 'private', 'manual', 'strategia', 'description')


class PortfolioInvestForm(forms.ModelForm):
    cash = forms.DecimalField(max_digits=10, decimal_places=2)
    date = forms.DateField()

    class Meta:
        model = PortfolioInvestHistory
        exclude = ['portfolio', 'cash_in_rub']


class RefreshPortfolio(forms.ModelForm):
    class Meta:
        model = InvestmentPortfolio
        fields = ['today_cash', 'private']
