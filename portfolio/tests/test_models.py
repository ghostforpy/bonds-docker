from django.test import TestCase
from decimal import Decimal
from django.utils.timezone import now
import datetime
from django.core.exceptions import ObjectDoesNotExist
from ..models import InvestmentPortfolio, PortfolioInvestHistory
from vklad.models import VkladInvestHistory
from bonds.users.models import User


class PortfolioTest(TestCase):
    """Base class for portfolio tests"""
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user = User.objects.create(username="user1", password="password1")


class RefreshChangesPortfolioTest(PortfolioTest):
    """Class for portfolio refresh_changes method tests"""

    def setUp(self):
        self.portfolio1 = InvestmentPortfolio.objects.create(
            owner=self.user,
            title="test_title1",
            manual=True,
            year_percent_profit=Decimal(12.5),
            previos_year_percent_profit=Decimal(11.5),
            percent_profit=Decimal(7.3),
            previos_percent_profit=Decimal(8.5),
            today_cash=Decimal(400000),
            previos_today_cash=Decimal(380000))
        self.portfolio2 = InvestmentPortfolio.objects.create(
            owner=self.user,
            title="test_title2",
            manual=False,
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


class PortfolioInvestHistoryTest(PortfolioTest):
    """Class for PortfolioInvestHistory methods tests"""

    def setUp(self):
        self.portfolio1 = InvestmentPortfolio.objects.create(
            owner=self.user,
            title="test_title1",
            manual=True,
            today_cash=Decimal(1000),
            ostatok=Decimal(1000))
        self.portfolio2 = InvestmentPortfolio.objects.create(
            owner=self.user,
            title="test_title2",
            manual=False,
            today_cash=Decimal(1000),
            ostatok=Decimal(1000))

    def test_action_in_save_method(self):
        """test normal actions"""
        portfolio = self.portfolio1
        new_instance = PortfolioInvestHistory(
            portfolio=portfolio,
            date=now().date())
        for action in ['vp', 'pv', 'tp', 'br', 'bc']:
            new_instance.action = action
            status = new_instance.save()
            self.assertNotEqual('wrong_action', status)
            self.assertEqual(
                new_instance,
                PortfolioInvestHistory.objects.get(id=new_instance.id))

        """test not normal actions,
        return status and raise ObjectDoesNotExist"""
        portfolio = self.portfolio2
        new_instance2 = PortfolioInvestHistory(
            portfolio=portfolio,
            date=now().date())
        for action in ['cc', 'dd']:
            new_instance2.action = action
            status = new_instance2.save()
            self.assertEqual('wrong_action', status)

            def f():
                return PortfolioInvestHistory.objects.get(portfolio=portfolio)
            self.assertRaises(ObjectDoesNotExist, f)

    def test_add_invest_to_portfolio(self):
        VkladInvestHistory.objects.create(
            vklad=self.user.vklad,
            date=now().date() - datetime.timedelta(days=1),
            cash=Decimal(2000),
            popolnenie=True)
        """test add invest to manual and not manual portfolios,
        test changes in vklad.ostatok"""
        for portfolio in [self.portfolio1, self.portfolio2]:
            new_instance = PortfolioInvestHistory(
                portfolio=portfolio,
                date=now().date() - datetime.timedelta(days=1),
                cash=Decimal(1000),
                action='vp')
            status = new_instance.save()
            self.assertEqual('ok', status)
            self.assertEqual(portfolio.ostatok, Decimal(2000))
            self.assertEqual(portfolio.today_cash, Decimal(2000))
            if portfolio == self.portfolio1:
                ostatok_vklad = Decimal(1000)
            else:
                ostatok_vklad = Decimal(0)
            self.assertEqual(self.user.vklad.ostatok, ostatok_vklad)
