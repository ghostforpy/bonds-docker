from django.db import models
from decimal import Decimal
from portfolio.models import InvestmentPortfolio
from django.core.exceptions import ObjectDoesNotExist
from bonds.users.models import User
from django.urls import reverse
# from datetime import datetime
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import threading
import django.dispatch
from .rshb import *
from .iss_simple_main import history as moex_history,\
    specification as moex_specification
# Create your models here.

refresh_price_security = django.dispatch.Signal(providing_args=["price"])
# Модель ценных бумаг


class Security(models.Model):
    name = models.CharField(max_length=50, unique=True)
    url = models.URLField(blank=True)
    security_type = models.CharField(max_length=20,
                                     default='bond',
                                     choices=[('pif_rshb', 'ОПИФ РСХБ'),
                                              ('ppif', 'БПИФ'),
                                              ('share', 'Акция'),
                                              ('bond', 'Облигация'),
                                              ('futures', 'Фьючерс'),
                                              ('index', 'Индекс'),
                                              ('etf_ppif', 'ETF'), ])
    parce_url = models.URLField(blank=True)
    code = models.CharField(max_length=30, blank=True, unique=True, null=True)
    shortname = models.CharField(max_length=50, blank=True, unique=True)
    fullname = models.CharField(max_length=100, blank=True, unique=True)
    regnumber = models.CharField(
        max_length=30, blank=True, unique=True, null=True)
    secid = models.CharField(max_length=30, blank=True, unique=True, null=True)
    isin = models.CharField(max_length=30, blank=True, unique=True, null=True)
    emitent = models.CharField(max_length=250, blank=True)
    board = models.CharField(max_length=250, blank=True)
    engine = models.CharField(max_length=250, blank=True)
    market = models.CharField(max_length=250, blank=True)
    description = models.CharField(max_length=250, blank=True)
    # Номинальная стоимость
    facevalue = models.DecimalField(max_digits=17, decimal_places=7,
                                    blank=True, default=0)
    # Первоначальная номинальная стоимость
    initialfacevalue = models.DecimalField(max_digits=17, decimal_places=7,
                                           blank=True, default=0)
    # Дата погашения
    matdate = models.DateField(blank=True, null=True)
    # Дата выплаты купона
    coupondate = models.DateField(blank=True, null=True)
    # Периодичность выплаты купона в год
    couponfrequency = models.IntegerField(blank=True, null=True)
    # Ставка купона, %
    couponpercent = models.DecimalField(max_digits=17, decimal_places=7,
                                        blank=True, null=True)
    # НКД для облигаций
    accint = models.DecimalField(max_digits=17, decimal_places=7,
                                 blank=True, null=True)
    # валюта номинала
    faceunit = models.CharField(max_length=20,
                                default='SUR',
                                choices=[('SUR', 'РУБ'),
                                         ('USD', 'USD'),
                                         ('EUR', 'EUR'),
                                         ('GBP', 'GBP'),
                                         ('CNY', 'CNY')],
                                blank=True)
    # Сумма купона, в валюте номинала
    couponvalue = models.DecimalField(max_digits=17, decimal_places=7,
                                      blank=True, null=True)
    today_price = models.DecimalField(max_digits=17, decimal_places=7,
                                      default=0)
    last_update = models.DateField(blank=True)
    oldest_date = models.DateField(blank=True)
    created = models.DateTimeField(auto_now_add=True,
                                   db_index=True)
    users_follows = models.ManyToManyField(User,
                                           related_name='security_followed',
                                           blank=True)
    # флаг отслеживания цен при ежедневном обновлении
    monitor = models.BooleanField(default=True)
    # процент изменения цены по сравнению с предыдущим значением
    # (предыдущим днем)
    change_price_percent = models.DecimalField(max_digits=10, decimal_places=3,
                                               default=0)

    class Meta:
        ordering = ['-last_update']

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
                try:
                    result = rshb(self.parce_url,
                                  date=self.last_update,
                                  first=first)
                except Exception:
                    return 'no data', self.today_price, self.last_update
                if result:
                    if not force and \
                            result['date_publication'] <= self.last_update:
                        return 'no new data',\
                            self.today_price,\
                            self.last_update
                    else:
                        self.change_price_percent = (
                            Decimal(result['price_today']) - self.today_price)\
                            / self.today_price * 100
                        self.last_update = result['date_publication']
                        self.today_price = result['price_today']
                        self.save()
                        refresh_price_security.send(
                            sender=self.__class__,
                            instance=self,
                            price=result['price_today'])
                        return 'ok',\
                            result['price_today'],\
                            result['date_publication']
                return 'no data', self.today_price, self.last_update
            return 'already update', self.today_price, self.last_update
        else:
            if force or self.last_update < now().date():
                try:
                    result = moex_history(self.parce_url)
                except Exception:
                    return 'no data', self.today_price, self.last_update
                days = [datetime.strptime(i, '%d.%m.%Y').date()
                        for i in result]
                if self.security_type == 'bond':
                    if self.matdate <= now().date():
                        self.monitor = False
                    if self.coupondate <= now().date():
                        # проверка параметров облигации
                        try:
                            description = moex_specification(self.secid)[0]
                            facevalue = description['FACEVALUE']
                            coupondate = description['COUPONDATE']
                            couponvalue = description['COUPONVALUE']
                            couponpercent = description['COUPONPERCENT']
                            if facevalue != self.facevalue:
                                self.facevalue = facevalue
                            if coupondate != self.coupondate:
                                self.coupondate = coupondate
                            if couponvalue != self.couponvalue:
                                self.couponvalue = couponvalue
                            if couponpercent != self.couponpercent:
                                self.couponpercent = couponpercent
                            self.save()
                        except Exception as e:
                            pass
                    for i in result:
                        result[i]['CLOSE'] = str(
                            float(result[i]['CLOSE']
                                  ) * float(self.facevalue) / 100)
                    self.accint = result[
                        datetime.strftime(max(days), '%d.%m.%Y')]['ACCINT']
                today_price = result[
                    datetime.strftime(max(days), '%d.%m.%Y')]['CLOSE']
                if not force and \
                        max(days) <= self.last_update:
                    return 'no new data', self.today_price, self.last_update
                else:
                    self.change_price_percent = (
                        Decimal(today_price) - self.today_price) / \
                        self.today_price * 100
                    self.last_update = max(days)
                    self.today_price = today_price
                    self.save()
                    # self.portfolios.all().update(
                    #    today_price=today_price)
                    refresh_price_security.send(
                        sender=self.__class__,
                        instance=self,
                        price=today_price)
                    return 'ok', today_price, max(days)
            return 'already update', self.today_price, self.last_update

    def get_history(self, date_since, date_until, format_result):
        if self.security_type == 'pif_rshb':
            try:
                result = rshb_history(self.parce_url,
                                      date_since,
                                      date_until,
                                      format_result=format_result)
            except Exception:
                return None
            return result
        else:
            result = moex_history(self.parce_url)
            history = {}
            if self.security_type == 'bond':
                for i in result:
                    history[i] = str(float(result[i]['CLOSE']
                                           ) * float(self.facevalue) / 100)
            else:
                for i in result:
                    history[i] = str(float(result[i]['CLOSE']))
            return history


class SecurityHistory(models.Model):
    name = models.ForeignKey(Security,
                             related_name='history',
                             on_delete=models.CASCADE,)
    date = models.DateField()
    price = models.DecimalField(max_digits=17, decimal_places=7,
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
    today_price = models.DecimalField(max_digits=17, decimal_places=7,
                                      default=0)
    total_cost = models.DecimalField(max_digits=17, decimal_places=7,
                                     default=0)

    class Meta:
        ordering = ['id']


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
    price = models.DecimalField(max_digits=17, decimal_places=7,
                                default=0)
    commission = models.DecimalField(max_digits=17, decimal_places=7,
                                     default=0)
    count = models.DecimalField(max_digits=20, decimal_places=7,
                                default=0)
    # НКД для покупки-продажи облигаций
    nkd = models.DecimalField(max_digits=20, decimal_places=7,
                              default=0)
    # при продаже бумаг учитывать НДФЛ
    ndfl = models.DecimalField(max_digits=20, decimal_places=7,
                               default=0)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # if self.security.security_type == 'bond':
            # if self.nkd == 0:
            #    return 'NKD must be more then 0'
        if self.buy:
            total_cost = self.price * self.count + self.commission + self.nkd
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
            total_cost = self.commission + self.count * self.price + self.ndfl
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
    else:
        try:
            s_p = SecurityPortfolios.objects.get(
                portfolio=portfolio,
                owner=owner,
                security=security)
        except ObjectDoesNotExist:
            return
        s_p.count += instance.count * (-1) ** (instance.buy)
    # в облигациях учитывать НКД
    if security.security_type == 'bond':
        s_p.total_cost = float(s_p.count) * \
            (float(s_p.today_price) + float(s_p.security.accint))
    else:
        s_p.total_cost = float(s_p.count) * float(s_p.today_price)
    s_p.save()
    if s_p.count == 0:
        s_p.delete()


@receiver(post_delete, sender=TradeHistory)
@receiver(post_save, sender=TradeHistory)
def refresh_portfolio_ostatok(sender, instance, created=False, **kwargs):
    portfolio = instance.portfolio
    total_cost = instance.price * instance.count + instance.nkd + \
        instance.commission * (-1) ** (not instance.buy) + \
        instance.ndfl * (-1) ** (not instance.buy)
    if created:
        portfolio.ostatok += total_cost * (-1) ** (instance.buy)
    else:
        portfolio.ostatok += total_cost * (-1) ** (not instance.buy)
    portfolio.save(update_fields=['ostatok'])
    portfolio.refresh_portfolio()


def upload(security, date, oldest_date):
    history = security.get_history(date, oldest_date, format_result='date')
    for i in history:
        newitem = SecurityHistory(name=security,
                                  date=i,
                                  price=history[i]['CLOSE'])
        newitem.save()


# @receiver(pre_save, sender=TradeHistory)
def upload_security_history(sender, instance, created=False, **kwargs):

    security = instance.security
    oldest_date = security.oldest_date
    date = instance.date
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
        i.today_price = security.today_price
        # в облигациях учитывать НКД
        if security.security_type == 'bond':
            i.total_cost = float(i.count) * \
                (float(i.today_price) + float(i.security.accint))
        else:
            i.total_cost = float(i.today_price) * float(i.count)
        i.save(update_fields=['today_price', 'total_cost'])
        i.portfolio.refresh_portfolio()


@receiver(post_delete, sender=TradeHistory)
@receiver(post_save, sender=TradeHistory)
def refresh_portfolio_previos_state(sender, instance, **kwargs):
    portfolio = instance.portfolio
    portfolio.previos_percent_profit = portfolio.percent_profit
    portfolio.previos_year_percent_profit = portfolio.year_percent_profit
    portfolio.previos_today_cash = portfolio.today_cash
    portfolio.save(update_fields=['change_year_percent_profit',
                                  'change_percent_profit',
                                  'change_today_cash'])
