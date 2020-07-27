from django.db import models
from bonds.users.models import User
from django.urls import reverse
from . import scripts

# Create your models here.


class InvestmentPortfolio(models.Model):
    owner = models.ForeignKey(User,
                              related_name='portfolios',
                              on_delete=models.CASCADE,)
    title = models.CharField(max_length=50)
    invest_cash = models.DecimalField(max_digits=10, decimal_places=2,
                                      default=0)
    today_cash = models.DecimalField(max_digits=10, decimal_places=2,
                                     default=0)
    ostatok = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    percent_profit = models.DecimalField(max_digits=5, decimal_places=2,
                                         default=0)
    year_percent_profit = models.DecimalField(max_digits=5, decimal_places=2,
                                              default=0)
    private = models.CharField(max_length=20,
                               default='da',
                               choices=[('da', 'deny_all'),
                                        ('af', 'allow_friends'),
                                        ('al', 'allow_login'),
                                        ('aa', 'allow_all')])
    manual = models.BooleanField(default=True)
    description = models.CharField(max_length=250, blank=True)
    strategia = models.CharField(max_length=20, blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    users_like = models.ManyToManyField(User,
                                        related_name='portfolio_liked',
                                        blank=True)
    total_likes = models.PositiveIntegerField(db_index=True, default=0,
                                              blank=True)
    users_follows = models.ManyToManyField(User,
                                           related_name='portfolio_followed',
                                           blank=True)
    total_followers = models.PositiveIntegerField(db_index=True, default=0,
                                                  blank=True)

    class Meta:
        ordering = ['id']

    def calc_percent_profit(self):
        try:
            self.percent_profit = scripts.percent_profit(self.today_cash,
                                                         self.invest_cash)
        except ZeroDivisionError:
            return
        # return scripts.percent_profit(self.today_cash,
        #                               self.invest_cash)

    def calc_year_percent_profit(self):
        t = self.portfolio_invests.filter(action__in=['pv', 'vp'])
        # t = PortfolioInvestHistory.objects.filter(portfolio=self.id)
        invest = [[i.cash * (-1)**(i.action == 'pv'), i.date] for i in t]
        self.year_percent_profit = scripts.year_percent_profit(
            invest, self.today_cash)
        # return scripts.year_percent_profit(invest, self.today_cash)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('portfolio:detail', args=[self.id])

    def calc_invest_cash_portfolio(self):
        t = self.portfolio_invests.exclude(action__in=['tp', 'br', 'bc'])
        self.invest_cash = sum([i.cash * (-1)**(i.action == 'pv') for i in t])

    def calc_today_cash(self):
        if not self.manual:
            securities = self.securities.all()
            total = sum([i.count * i.today_price for i in securities])
            self.today_cash = total + self.ostatok
            self.save(update_fields=['today_cash'])
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        super(InvestmentPortfolio, self).save(*args, **kwargs)

    def refresh_portfolio(self):
        self.calc_today_cash()
        self.calc_invest_cash_portfolio()
        self.calc_percent_profit()
        self.calc_year_percent_profit()
        self.save()
        self.owner.vklad.refresh_vklad()


class PortfolioHistory(models.Model):
    portfolio = models.ForeignKey(InvestmentPortfolio,
                                  on_delete=models.CASCADE)
    date = models.DateField()
    percent_profit = models.DecimalField(max_digits=5,
                                         decimal_places=2, default=0)
    year_percent_profit = models.DecimalField(max_digits=5,
                                              decimal_places=2, default=0)

    class Meta:
        ordering = ['-date']

    def calc_percent_profit(self):
        pass

    def calc_year_percent_profit(self):
        pass


class PortfolioInvestHistory(models.Model):
    portfolio = models.ForeignKey(InvestmentPortfolio,
                                  related_name='portfolio_invests',
                                  on_delete=models.CASCADE)
    date = models.DateField()
    cash = models.DecimalField(max_digits=10,
                               decimal_places=2, default=0)
    action = models.CharField(max_length=20,
                              default='vklad_to_portfolio',
                              choices=[('vp', 'На портфель'),
                                       ('pv', 'На вклад'),
                                       ('tp', 'Доход'),
                                       ('bc', 'Комиссия брокера'),
                                       ('br',
                                        'Частичное погашение облигаций')])
    # при получении дохода учитыавть НДФЛ
    ndfl = models.DecimalField(max_digits=10,
                               decimal_places=2, default=0)
    # при получении дохода можно выбрать по какой бумаге получен доход
    security = models.ForeignKey('moex.Security',
                                 on_delete=models.SET_NULL,
                                 blank=True,
                                 null=True)

    class Meta:
        ordering = ['-date', 'cash']

    def save(self, *args, **kwargs):
        if self.action not in ['vp',
                               'pv',
                               'tp',
                               'br',
                               'bc']:
            return 'wrong_action'
        if self.action == 'vp':
            # Пополнение с вклада происходит только,
            # если на остатке вклада имеются деньги
            if self.portfolio.owner.vklad.ostatok >= self.cash:
                self.portfolio.owner.vklad.ostatok -= self.cash
                self.portfolio.ostatok += self.cash
                # без автоматического подсчета меняем today_cash руками
                if self.portfolio.manual:
                    self.portfolio.today_cash += self.cash
            else:
                return 'no money on vklad'
        if self.action == 'pv':
            # Снятие денег(перевод на вклад) происходит только,
            # если на остатке портфеля есть деньги
            if self.cash > self.portfolio.ostatok:
                return 'no money on portfolio'
            else:
                self.portfolio.owner.vklad.ostatok += self.cash
                self.portfolio.owner.vklad.save()
                self.portfolio.ostatok -= self.cash
                # без автоматического подсчета меняем today_cash руками
                if self.portfolio.manual:
                    self.portfolio.today_cash -= self.cash
        if self.action in ['tp', 'br']:
            # Запись о начислении дивидендов/купонов и т.д.
            # или о частичном погашении облигаций
            self.portfolio.ostatok += self.cash - self.ndfl
            # без автоматического подсчета меняем today_cash руками
            if self.portfolio.manual:
                self.portfolio.today_cash += self.cash - self.ndfl
        if self.action == 'bc':
            self.portfolio.ostatok -= self.cash
        super(PortfolioInvestHistory, self).save(*args, **kwargs)
        self.portfolio.refresh_portfolio()
        return 'ok'

    def delete(self, *args, **kwargs):
        if self.action == 'pv':
            if self.portfolio.owner.vklad.ostatok >= self.cash:
                self.portfolio.ostatok += self.cash
                # без автоматического подсчета меняем today_cash руками
                if self.portfolio.manual:
                    self.portfolio.today_cash += self.cash
                self.portfolio.owner.vklad.ostatok -= self.cash
            else:
                return 'no money on vklad'
        elif self.action == 'vp':
            if self.portfolio.ostatok >= self.cash:
                self.portfolio.ostatok -= self.cash
                # без автоматического подсчета меняем today_cash руками
                if self.portfolio.manual:
                    self.portfolio.today_cash -= self.cash
                self.portfolio.owner.vklad.ostatok += self.cash
            else:
                return 'no money on portfolio'
        elif self.action in ['tp', 'br']:
            if self.portfolio.ostatok >= self.cash:
                self.portfolio.ostatok -= self.cash + self.ndfl
                # без автоматического подсчета меняем today_cash руками
                if self.portfolio.manual:
                    self.portfolio.today_cash -= self.cash + self.ndfl
            else:
                return 'no money on portfolio'
        if self.action == 'bc':
            self.portfolio.ostatok += self.cash
        super(PortfolioInvestHistory, self).delete(*args, **kwargs)
        self.portfolio.refresh_portfolio()
        return 'ok'
