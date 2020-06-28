from django.db import models
from portfolio.models import InvestmentPortfolio
from django.core.exceptions import ObjectDoesNotExist
from bonds.users.models import User
from django.urls import reverse
# from datetime import datetime
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
import threading
import django.dispatch
from .rshb import *
# Create your models here.

refresh_price_security = django.dispatch.Signal(providing_args=["price"])
# Модель ценных бумаг


class Security(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(blank=True)
    security_type = models.CharField(max_length=20,
                                     default='bond',
                                     choices=[('pif_rshb', 'ОПИФ РСХБ'),
                                              ('bpif', 'БПИФ'),
                                              ('stock', 'Акция'),
                                              ('bond', 'Облигация')])
    parce_url = models.URLField(blank=True)
    code = models.CharField(max_length=30, blank=True)
    shortname = models.CharField(max_length=50, blank=True)
    fullname = models.CharField(max_length=100, blank=True)
    regnumber = models.CharField(max_length=30, blank=True)
    secid = models.CharField(max_length=30, blank=True)
    isin = models.CharField(max_length=30, blank=True)
    emitent = models.CharField(max_length=250, blank=True)
    description = models.CharField(max_length=250, blank=True)
    today_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      default=0)
    last_update = models.DateField(blank=True)
    oldest_date = models.DateField(blank=True)
    created = models.DateTimeField(auto_now_add=True,
                                   db_index=True)
    users_follows = models.ManyToManyField(User,
                                           related_name='security_followed',
                                           blank=True)

    def get_absolute_url(self):
        return reverse('moex:detail', args=[self.id])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Security, self).save(*args, **kwargs)
        # portfolios_for_refresh = self.portfolios.all()
        # for item in portfolios_for_refresh:
        #     item.portfolio.refresh_portfolio()

    def refresh_price(self, first=False, force=False):
        if self.security_type == 'pif_rshb':
            if force or self.last_update < now().date():
                result = rshb(self.parce_url,
                              date=self.last_update,
                              first=first)
                if result:
                    history = self.history.filter(date=result['date_today'])
                    if history.count():
                        pass
                    else:
                        '''
                        newitem = SecurityHistory(name=self,
                                                  date=result['date_today'],
                                                  price=result['price_today'])
                        newitem.save()
                        '''
                        self.last_update = result['date_publication']
                        self.today_price = result['price_today']
                        self.save()
                        self.portfolios.all().update(
                            today_price=result['price_today'])
                        refresh_price_security.send(
                            sender=self.__class__,
                            instance=self,
                            price=result['price_today'])
                        return 'ok', result['price_today']
                return 'no data', self.today_price
            return 'already update', self.today_price

    def get_history(self, date_since, date_until, format_result):
        if self.security_type == 'pif_rshb':
            result = rshb_history(self.parce_url,
                                  date_since,
                                  date_until,
                                  format_result=format_result)
            return result


class SecurityHistory(models.Model):
    name = models.ForeignKey(Security,
                             related_name='history',
                             on_delete=models.CASCADE,)
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                default=0)
    percent_prev_date = models.DecimalField(max_digits=10, decimal_places=2,
                                            default=0)

    def save(self, *args, **kwargs):
        history = SecurityHistory.objects.filter(
            name=self.name, date=self.date)
        if not history:
            super(SecurityHistory, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-date']


class SecurityPortfolios(models.Model):
    owner = models.ForeignKey(User,
                              related_name='securities',
                              on_delete=models.CASCADE,)
    portfolio = models.ForeignKey(InvestmentPortfolio,
                                  related_name='securities',
                                  on_delete=models.CASCADE,)
    security = models.ForeignKey(Security,
                                 related_name='portfolios',
                                 on_delete=models.CASCADE,)
    count = models.DecimalField(max_digits=20, decimal_places=7,
                                default=0)
    today_price = models.DecimalField(max_digits=10, decimal_places=2,
                                      default=0)


class TradeHistory(models.Model):
    owner = models.ForeignKey(User,
                              related_name='trades',
                              on_delete=models.CASCADE,)
    portfolio = models.ForeignKey(InvestmentPortfolio,
                                  related_name='trade_securities',
                                  on_delete=models.CASCADE,)
    security = models.ForeignKey(Security,
                                 related_name='trades',
                                 on_delete=models.CASCADE,)
    date = models.DateField()
    # buy - True, sell - False
    buy = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                default=0)
    commission = models.DecimalField(max_digits=10, decimal_places=2,
                                     default=0)
    count = models.DecimalField(max_digits=20, decimal_places=7,
                                default=0)

    def save(self, *args, **kwargs):
        if self.buy:
            total_cost = self.price * self.count + self.commission
            if total_cost > self.portfolio.ostatok:
                return 'no money on portfolio.ostatok'
            else:
                super(TradeHistory, self).save(*args, **kwargs)
                return 'ok'
        else:
            try:
                security_portfolios = self.portfolio.securities.get(
                    security=self.security)
                count_security_in_portfolio = security_portfolios.count
            except ObjectDoesNotExist:
                count_security_in_portfolio = 0
            if self.count > count_security_in_portfolio:
                return 'no security on portfolio'
            else:
                super(TradeHistory, self).save(*args, **kwargs)
                return 'ok'

    def delete(self, *args, **kwargs):
        try:
            s_p = SecurityPortfolios.objects.get(portfolio=self.portfolio,
                                                 security=self.security)
        except ObjectDoesNotExist:
            return 'no delete'
        if self.buy:
            if self.count <= s_p.count:
                super(TradeHistory, self).delete(*args, **kwargs)
                return 'ok'
            else:
                return 'need more security in portfolio'
        else:
            total_cost = self.commission + self.count * self.price
            if self.portfolio.ostatok < total_cost:
                return 'need more money on portfolio ostatok'
            else:
                super(TradeHistory, self).delete(*args, **kwargs)
                return 'ok'


@receiver(post_delete, sender=TradeHistory)
@receiver(post_save, sender=TradeHistory)
def refresh_count_security_in_portfolio(sender,
                                        instance,
                                        created=False,
                                        **kwargs):
    portfolio = instance.portfolio
    owner = instance.owner
    security = instance.security
    if created:
        s_p, s_p_created = SecurityPortfolios.objects.get_or_create(
            portfolio=portfolio,
            owner=owner,
            security=security)
        if s_p_created:
            s_p.count = 0
        s_p.count += instance.count * (-1) ** (not instance.buy)
        s_p.today_price = security.today_price
        s_p.save(update_fields=['count', 'today_price'])
    else:
        try:
            s_p = SecurityPortfolios.objects.get(
                portfolio=portfolio,
                owner=owner,
                security=security)
        except ObjectDoesNotExist:
            return
        s_p.count += instance.count * (-1) ** (instance.buy)
        s_p.save(update_fields=['count'])


@receiver(post_delete, sender=TradeHistory)
@receiver(post_save, sender=TradeHistory)
def refresh_portfolio_ostatok(sender, instance, created=False, **kwargs):
    portfolio = instance.portfolio
    total_cost = instance.price * instance.count + \
        instance.commission * (-1) ** (not instance.buy)
    if created:
        portfolio.ostatok += total_cost * (-1) ** (instance.buy)
        portfolio.save(update_fields=['ostatok'])
        portfolio.refresh_portfolio()
    else:
        portfolio.ostatok += total_cost * (-1) ** (not instance.buy)
        portfolio.save(update_fields=['ostatok'])
        portfolio.refresh_portfolio()


def upload(security, date, oldest_date):
    history = security.get_history(date, oldest_date, format_result='date')
    for i in history:
        newitem = SecurityHistory(name=security,
                                  date=i,
                                  price=history[i])
        newitem.save()


# @receiver(pre_save, sender=TradeHistory)
def upload_security_history(sender, instance, created=False, **kwargs):

    security = instance.security
    oldest_date = security.oldest_date
    date = instance.date
    #print(oldest_date, date)
    if oldest_date > date:
        security.oldest_date = instance.date
        security.save(update_fields=['oldest_date'])
        t = threading.Thread(target=upload, args=(security,
                                                  date,
                                                  oldest_date,))
        t.start()


@receiver(refresh_price_security, sender=Security)
def refresh_portfolios(sender, instance, **kwargs):
    security = instance
    s_p = security.portfolios.all()
    for i in s_p:
        i.portfolio.refresh_portfolio()
