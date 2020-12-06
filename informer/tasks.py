from config.settings.base import env
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from moex.models import SecurityPortfolios
#from django.utils.html import strip_tags

from config import celery_app
from moex.utils import get_followed_securities_by_user,\
    get_securities_in_portfolios_by_user

User = get_user_model()
DEFAULT_FROM_EMAIL = env(
    "DJANGO_SERVER_EMAIL", default="bonds <noreply@mybonds.space>"
)


@celery_app.task(bind=True,
                 name='user.informer')
def informer(self, exclude_emails=None, *args, **kwargs):
    users = User.objects.\
        filter(is_active=True).\
        exclude(email__in=args).\
        filter(informer__enable__exact=True)
    if exclude_emails:
        users = users.exclude(email__in=exclude_emails)
    result = dict()
    for user in users:
        result[user.email] = dict()
        portfolios = user.portfolios.all()
        securities_in_portfolios = get_securities_in_portfolios_by_user(user)
        security_followed = get_followed_securities_by_user(user)
        result[user.email]['securities_in_portfolios'] = [
            i.name for i in securities_in_portfolios]
        result[user.email]['security_followed'] = [
            i.name for i in security_followed]
        portfolio_followed = user.portfolio_followed.all()
        if not portfolios and \
                not securities_in_portfolios and \
                not security_followed and \
                not portfolio_followed:
            continue
        html_message = render_to_string(
            'users/email_informer_template.html',
            {'portfolios': portfolios,
             'portfolio_followed': portfolio_followed,
             'securities_in_portfolios': securities_in_portfolios,
             'security_followed': security_followed, })
        subject = 'Информация о состоянии ваших портфелей и\
        отслеживаемых ценных бумагах'
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=html_message)
    return result
