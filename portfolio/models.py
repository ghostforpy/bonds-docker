from django.db import models
from bonds.users.models import User
from django.urls import reverse
from decimal import Decimal, DivisionByZero
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
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
    previos_today_cash = models.DecimalField(max_digits=10, decimal_places=2,
                                             default=0)
    change_today_cash = models.DecimalField(max_digits=5,
                                            decimal_places=2,
                                            default=0)
    ostatok = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    percent_profit = models.DecimalField(max_digits=5, decimal_places=2,
                                         default=0)
    previos_percent_profit = models.DecimalField(max_digits=5,
                                                 decimal_places=2,
                                                 default=0)
    change_percent_profit = models.DecimalField(max_digits=5, decimal_places=2,
                                                default=0)
    year_percent_profit = models.DecimalField(max_digits=5, decimal_places=2,
                                              default=0)
    previos_year_percent_profit = models.DecimalField(max_digits=5,
                                                      decimal_places=2,
                                                      default=0)
    change_year_percent_profit = models.DecimalField(max_digits=5,
                                                     decimal_places=2,
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
            percent_profit = scripts.percent_profit(self.today_cash,
                                                    self.invest_cash)
            self.percent_profit = percent_profit
        except ZeroDivisionError:
            return

    def calc_year_percent_profit(self):
        # выбор записей пополнения и снятия денег
        t = self.portfolio_invests.filter(action__in=['pv', 'vp'])
        # формирование списка инвестиций и снятий денег с датами
        invest = [[i.cash * (-1)**(i.action == 'pv'), i.date] for i in t]
        year_percent_profit = scripts.year_percent_profit(
            invest, self.today_cash)
        self.year_percent_profit = year_percent_profit

    def __str__(self):
        return self.title

    def request_user_has_permission(self, request_user, check_owner=True):
        if check_owner and request_user == self.owner:
            return True
        if self.private == 'da':
            return False
        if self.private == 'aa':
            return True
        if self.private == 'al':
            return request_user.is_authenticated
        if self.private == 'af':
            if request_user.is_authenticated:
                return request_user.friends.is_friend(
                    self.owner.friends)
            else:
                return False

    def get_absolute_url(self):
        return reverse('portfolio:detail', args=[self.id])

    def calc_invest_cash_portfolio(self):
        # выбор записей пополнения и снятия денег
        t = self.portfolio_invests.filter(action__in=['pv', 'vp'])
        self.invest_cash = sum([i.cash * (-1)**(i.action == 'pv') for i in t])

    def calc_today_cash(self):
        if not self.manual:
            securities = self.securities.all()
            total = sum([i.total_cost_in_rub for i in securities])
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

    def refresh_portfolio_changes(self):
        change_year_percent_profit = (
            Decimal(self.year_percent_profit
                    ) - Decimal(self.previos_year_percent_profit))
        self.previos_year_percent_profit = self.year_percent_profit
        self.change_year_percent_profit = change_year_percent_profit
        change_percent_profit = (
            Decimal(self.percent_profit
                    ) - Decimal(self.previos_percent_profit))
        self.previos_percent_profit = self.percent_profit
        self.change_percent_profit = change_percent_profit
        try:
            change_today_cash = (
                Decimal(self.today_cash) - Decimal(self.previos_today_cash)
            ) / Decimal(self.previos_today_cash) * 100
        except DivisionByZero:
            change_today_cash = 0
        self.previos_today_cash = self.today_cash
        self.change_today_cash = change_today_cash
        self.save()


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
                              choices=[('vp', 'Пополнение'),
                                       ('pv', 'Снятие'),
                                       ('tp', 'Доход'),
                                       ('bc', 'Комиссия брокера'),
                                       ('br',
                                        'Частичное погашение облигаций'),
                                       ('tax',
                                        'Налог на доход')])
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
                               'bc',
                               'tax']:
            return 'wrong_action'
        if self.action == 'vp':
            # Увеличиваем остаток на величину
            # внесенных денег
            self.portfolio.ostatok += self.cash
            # без автоматического подсчета меняем today_cash руками
            if self.portfolio.manual:
                self.portfolio.today_cash += self.cash
        if self.action == 'pv':
            # Снятие денег(перевод на вклад) происходит только,
            # если на остатке портфеля есть деньги
            if self.cash > self.portfolio.ostatok:
                return 'no money on portfolio'
            else:
              #  self.portfolio.owner.vklad.ostatok += self.cash
              #  self.portfolio.owner.vklad.save()
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
        # снятие денег при оплате комисси брокеру за обслуживание счета
        # или при уплате налога на доход, когда он не был уплачен ранее
        if self.action in ['bc', 'tax']:
            self.portfolio.ostatok -= self.cash
            # без автоматического подсчета меняем today_cash руками
            if self.portfolio.manual:
                self.portfolio.today_cash -= self.cash
        super(PortfolioInvestHistory, self).save(*args, **kwargs)
        self.portfolio.refresh_portfolio()
        return 'ok'

    def delete(self, *args, **kwargs):
        # удаление записи о снятии денежных средств
        if self.action == 'pv':
            # if self.portfolio.owner.vklad.ostatok >= self.cash:
            self.portfolio.ostatok += self.cash
            # без автоматического подсчета меняем today_cash руками
            if self.portfolio.manual:
                self.portfolio.today_cash += self.cash
              #  self.portfolio.owner.vklad.ostatok -= self.cash
            # else:
             #   return 'no money on vklad'
        # удаление записи о внесении денежных средств
        elif self.action == 'vp':
            if self.portfolio.ostatok >= self.cash:
                self.portfolio.ostatok -= self.cash
                # без автоматического подсчета меняем today_cash руками
                if self.portfolio.manual:
                    self.portfolio.today_cash -= self.cash
              #  self.portfolio.owner.vklad.ostatok += self.cash
            else:
                return 'no money on portfolio'
        # удаление записи о получении дохода или частичном погашении облигаций
        elif self.action in ['tp', 'br']:
            if self.portfolio.ostatok >= self.cash:
                self.portfolio.ostatok -= self.cash + self.ndfl
                # без автоматического подсчета меняем today_cash руками
                if self.portfolio.manual:
                    self.portfolio.today_cash -= self.cash + self.ndfl
            else:
                return 'no money on portfolio'
        # удаление записи об уплате комиссии брокера, налога на доход
        if self.action in ['bc', 'tax']:
            self.portfolio.ostatok += self.cash
            # без автоматического подсчета меняем today_cash руками
            if self.portfolio.manual:
                self.portfolio.today_cash += self.cash
        super(PortfolioInvestHistory, self).delete(*args, **kwargs)
        self.portfolio.refresh_portfolio()
        return 'ok'


@receiver(post_delete, sender=PortfolioInvestHistory)
@receiver(post_save, sender=PortfolioInvestHistory)
def refresh_portfolio_previos_state(sender, instance, **kwargs):
    portfolio = instance.portfolio
    portfolio.previos_percent_profit = portfolio.percent_profit
    portfolio.previos_year_percent_profit = portfolio.year_percent_profit
    portfolio.previos_today_cash = portfolio.today_cash
    portfolio.save(update_fields=['change_year_percent_profit',
                                  'change_percent_profit',
                                  'change_today_cash'])
