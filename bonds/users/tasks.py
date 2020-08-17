from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string
from moex.models import SecurityPortfolios
#from django.utils.html import strip_tags

from config import celery_app

User = get_user_model()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@celery_app.task(bind=True,
                 name='user.informer')
def informer(self, *args):
    users = User.objects.filter(is_active=True).exclude(email__in=args)
    result = dict()
    for user in users:
        portfolios = user.portfolios.all()
        if not portfolios:
            continue
        s_p = SecurityPortfolios.objects.filter(portfolio__in=portfolios)
        securities_in_portfolios = [i.security for i in s_p]
        security_followed = [i for i in user.security_followed.all(
        ) if i not in securities_in_portfolios]
        result[user.email] = dict()
        result[user.email]['securities_in_portfolios'] = [
            i.name for i in securities_in_portfolios]
        result[user.email]['security_followed'] = [
            i.name for i in security_followed]
        html_message = render_to_string(
            'users/email_informer_template.html', {'portfolios': portfolios,
                                                   'securities_in_portfolios':
                                                   securities_in_portfolios,
                                                   'security_followed':
                                                   security_followed, })
        subject = 'Информация о состоянии ваших портфелей и отслеживаемых ценных бумагах'
        send_mail(
            subject,
            '',
            'info@mybonds.space',
            [user.email],
            fail_silently=False,
            html_message=html_message)
    return result
