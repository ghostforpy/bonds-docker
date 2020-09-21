from django.db import models
from bonds.users.models import User
from django.urls import reverse
from portfolio import scripts
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Prefetch
from portfolio.models import PortfolioInvestHistory
# Create your models here.


class UserVklad(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name='vklad')
    invest_cash = models.DecimalField(max_digits=10, decimal_places=2,
                                      default=0)
    today_cash = models.DecimalField(max_digits=10, decimal_places=2,
                                     default=0)
    ostatok = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    percent_profit = models.DecimalField(max_digits=5, decimal_places=2,
                                         default=0)
    year_percent_profit = models.DecimalField(max_digits=5, decimal_places=2,
                                              default=0)

    def calc_invest_cash(self):
        user = self.owner
        self.invest_cash = sum(
            [i.invest_cash for i in user.portfolios.all()]
        )

    def calc_percent_profit(self):
        self.percent_profit = scripts.percent_profit(self.today_cash,
                                                     self.invest_cash)

    def calc_today_cash(self):
        t = self.owner.portfolios.all()
        total = [i.today_cash for i in t]
        self.today_cash = sum(total)

    def calc_year_percent_profit(self):
        portfolios = self.owner.portfolios.all()
        queryset = PortfolioInvestHistory.objects.filter(
            action__in=['vp', 'pv'])
        prefecth = Prefetch('portfolio_invests',
                            queryset=queryset,
                            to_attr='invests')
        portfolio_invests = portfolios.prefetch_related(prefecth)
        res = [item for sublist in portfolio_invests
               for item in sublist.invests]
        invests = [[i.cash * (-1)**(i.action == 'pv'), i.date] for i in res]
        self.year_percent_profit = scripts.year_percent_profit(
            invests, self.today_cash)

    def refresh_vklad(self):
        self.calc_invest_cash()
        self.calc_today_cash()
        try:
            self.calc_percent_profit()
        except ZeroDivisionError:
            return
        self.calc_year_percent_profit()
        self.save()

    def get_absolute_url(self):
        return reverse('vklad:detail_vklad')


@receiver(post_save, sender=User)
def create_user_vklad(sender, instance, created, **kwargs):
    if created:
        UserVklad.objects.create(owner=instance)


class VkladHistory(models.Model):
    vklad = models.ForeignKey(UserVklad, on_delete=models.CASCADE,
                              related_name='vklad_historyes')
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


class VkladInvestHistory(models.Model):
    vklad = models.ForeignKey(
        UserVklad, related_name='vklads', on_delete=models.CASCADE)
    date = models.DateField()
    cash = models.DecimalField(max_digits=10,
                               decimal_places=2, default=0)
    popolnenie = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.popolnenie:
            if self.cash > self.vklad.ostatok:
                return 'no money'
            self.vklad.ostatok -= self.cash
        else:
            self.vklad.ostatok += self.cash
        super(VkladInvestHistory, self).save(*args, **kwargs)
        self.vklad.refresh_vklad()
        return 'ok'

    def delete(self, *args, **kwargs):
        if self.popolnenie:
            if self.cash <= self.vklad.ostatok:
                self.vklad.ostatok -= self.cash
            else:
                return 'no_money'
        else:
            self.vklad.ostatok += self.cash
        super(VkladInvestHistory, self).delete(*args, **kwargs)
        self.vklad.refresh_vklad()
        return 'ok'

    class Meta:
        ordering = ['-date', 'cash']
