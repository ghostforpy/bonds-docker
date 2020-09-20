from django.test import TestCase
from decimal import Decimal
from django.utils.timezone import now
import datetime
from django.core.exceptions import ObjectDoesNotExist
from ..models import *
from portfolio.models import InvestmentPortfolio, PortfolioInvestHistory
#from vklad.models import VkladInvestHistory
from bonds.users.models import User


class VkladTest(TestCase):
    """Base class for portfolio tests"""
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.user = User.objects.create(username="user1", password="password1")
    
    def setUp(self):
        self.portfolio1 = InvestmentPortfolio.objects.create(
            owner=self.user,
            title="test_title1",
            manual=True
            )
        self.portfolio2 = InvestmentPortfolio.objects.create(
            owner=self.user,
            title="test_title2",
            manual=False
            )
        

class AddInvestsInPortfolioTest1(VkladTest):
    """Class for tests add invests in user portfolios,
    test input,output invests"""

    def test_input_output_invest_function(self):
        vklad = self.user.vklad
        self.assertEqual(vklad.invest_cash, Decimal(0))
        self.assertEqual(vklad.today_cash, Decimal(0))

        new_instance1 = PortfolioInvestHistory.objects.create(
            portfolio=self.portfolio1,
            cash=Decimal(1000),
            action='vp',
            date=now().date() - datetime.timedelta(days=1)          
        )
        self.assertEqual(vklad.invest_cash, Decimal(1000))
        self.assertEqual(vklad.today_cash, Decimal(1000))

        new_instance2 = PortfolioInvestHistory.objects.create(
            portfolio=self.portfolio2,
            cash=Decimal(2000),
            action='vp',
            date=now().date() - datetime.timedelta(days=1)          
        )
        self.assertEqual(vklad.invest_cash, Decimal(3000))
        self.assertEqual(vklad.today_cash, Decimal(3000))

        new_instance3 = PortfolioInvestHistory.objects.create(
            portfolio=self.portfolio1,
            cash=Decimal(1000),
            action='pv',
            date=now().date() - datetime.timedelta(days=1)          
        )
        self.assertEqual(vklad.invest_cash, Decimal(2000))
        self.assertEqual(vklad.today_cash, Decimal(2000))

        new_instance4 = PortfolioInvestHistory.objects.create(
            portfolio=self.portfolio2,
            cash=Decimal(500),
            action='pv',
            date=now().date() - datetime.timedelta(days=1)          
        )
        self.assertEqual(vklad.invest_cash, Decimal(1500))
        self.assertEqual(vklad.today_cash, Decimal(1500))

class AddInvestsInPortfolioTest2(VkladTest):
    """Class for tests add invests in user portfolios,
    test other actions invests"""
    def test_add_invest_no_input_output(self):
        vklad = self.user.vklad
        new_instance1 = PortfolioInvestHistory.objects.create(
            portfolio=self.portfolio1,
            cash=Decimal(1000),
            action='vp',
            date=now().date() - datetime.timedelta(days=1)          
        )
        for action in ['tp', 'br', 'bc', 'tax']:
            new_instance1 = PortfolioInvestHistory.objects.create(
                portfolio=self.portfolio1,
                cash=Decimal(100),
                action=action,
                date=now().date()          
            )
            self.assertEqual(vklad.invest_cash, Decimal(1000))
            if action == 'tp':
                self.assertEqual(vklad.today_cash, Decimal(1100))
            if action == 'br':
                self.assertEqual(vklad.today_cash, Decimal(1200))
            if action == 'bc':
                self.assertEqual(vklad.today_cash, Decimal(1100))
            if action == 'tax':
                self.assertEqual(vklad.today_cash, Decimal(1000))
       
            
class CalcInvestCash(VkladTest):
    """Test calc_invest_cash_function"""
    def test(self):
        vklad = self.user.vklad
        temp = 0
        for i in range(10):
            new_instance1 = PortfolioInvestHistory.objects.create(
                portfolio=self.portfolio1,
                cash=1000*i,
                action='vp',
                date=now().date() - datetime.timedelta(days=i)
            )
            new_instance2 = PortfolioInvestHistory.objects.create(
                portfolio=self.portfolio2,
                cash=500*i,
                action='vp',
                date=now().date() - datetime.timedelta(days=2*i)
            )
            temp += 1000 * i + 500 * i
        self.assertEqual(vklad.invest_cash, Decimal(temp))
        self.assertEqual(vklad.today_cash, Decimal(temp))
        
        for i in range(5):
            new_instance1 = PortfolioInvestHistory.objects.create(
                portfolio=self.portfolio1,
                cash=100*i,
                action='pv',
                date=now().date() - datetime.timedelta(days=i)
            )
            new_instance2 = PortfolioInvestHistory.objects.create(
                portfolio=self.portfolio2,
                cash=50*i,
                action='pv',
                date=now().date() - datetime.timedelta(days=2*i)
            )
            temp -= 100 * i + 50 * i
        self.assertEqual(vklad.invest_cash, Decimal(temp))
        self.assertEqual(vklad.today_cash, Decimal(temp))
        temp1 = 0
        for i in range(3):
            new_instance1 = PortfolioInvestHistory.objects.create(
                portfolio=self.portfolio1,
                cash=20*i,
                action='tp',
                date=now().date() - datetime.timedelta(days=i)
            )
            new_instance2 = PortfolioInvestHistory.objects.create(
                portfolio=self.portfolio2,
                cash=15*i,
                action='tp',
                date=now().date() - datetime.timedelta(days=2*i)
            )
            temp1 += 20 * i + 15 * i
        self.assertEqual(vklad.invest_cash, Decimal(temp))
        self.assertEqual(vklad.today_cash, Decimal(temp + temp1))

        self.assertEqual(vklad.year_percent_profit, Decimal(6.8))
        self.assertEqual(vklad.percent_profit, Decimal(0.16))