from django.test import TestCase
from decimal import Decimal
from ..models import InvestmentPortfolio
from bonds.users.models import User


class RefreshChangesPortfolioTest(TestCase):
    """docstring for RefreshChangesPortfolioTest"""
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user = User.objects.create(username="user1", password="password1")

    def setUp(self):
        self.portfolio1 = InvestmentPortfolio.objects.create(
            owner=self.user,
            title="test_title1",
            year_percent_profit=Decimal(12.5),
            previos_year_percent_profit=Decimal(11.5),
            percent_profit=Decimal(7.3),
            previos_percent_profit=Decimal(8.5),
            today_cash=Decimal(400000),
            previos_today_cash=Decimal(380000))
        self.portfolio2 = InvestmentPortfolio.objects.create(
            owner=self.user,
            title="test_title2",
            year_percent_profit=Decimal(12.5),
            previos_year_percent_profit=Decimal(0),
            percent_profit=Decimal(7.3),
            previos_percent_profit=Decimal(0),
            today_cash=Decimal(400000),
            previos_today_cash=Decimal(0))

    def test_refresh_changes_function(self):
        self.portfolio1.refresh_portfolio_changes()
        self.assertEqual(
            self.portfolio1.previos_year_percent_profit, Decimal(12.5))
        self.assertEqual(
            self.portfolio1.previos_percent_profit, Decimal(7.3))
        self.assertEqual(
            self.portfolio1.previos_today_cash, Decimal(400000))
        self.assertEqual(
            self.portfolio1.change_year_percent_profit.quantize(
                Decimal("1.00")),
            Decimal(1).quantize(Decimal("1.00")))
        self.assertEqual(
            self.portfolio1.change_percent_profit.quantize(Decimal("1.00")),
            Decimal(-1.2).quantize(Decimal("1.00")))
        self.assertEqual(
            self.portfolio1.change_today_cash.quantize(Decimal("1.00")),
            Decimal(
                (400000 - 380000) / 380000 * 100).quantize(Decimal("1.00")))

    def test_refresh_changes_function_new_portfolio(self):
        self.portfolio2.refresh_portfolio_changes()
        self.assertEqual(
            self.portfolio2.previos_year_percent_profit, Decimal(12.5))
        self.assertEqual(
            self.portfolio2.previos_percent_profit, Decimal(7.3))
        self.assertEqual(
            self.portfolio2.previos_today_cash, Decimal(400000))
        self.assertEqual(
            self.portfolio2.change_year_percent_profit.quantize(
                Decimal("1.00")),
            Decimal(12.5).quantize(Decimal("1.00")))
        self.assertEqual(
            self.portfolio2.change_percent_profit.quantize(Decimal("1.00")),
            Decimal(7.3).quantize(Decimal("1.00")))
        self.assertEqual(self.portfolio1.change_today_cash, Decimal(0))
