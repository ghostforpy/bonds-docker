from .models import Security

from config import celery_app
from django.utils.timezone import now


@celery_app.task(bind=True,
                 name='moex.refresh_security',
                 default_retry_delay=30 * 60,
                 max_retries=6)
def refresh_security(self):
    today = now().date()
    securities = Security.objects.filter(last_update__lt=today)
    result = dict()
    for security in securities:
        result[security.name] = security.refresh_price()
    if securities.count():
        if securities.count() > len(
                [i for i in result if 'ok' == result[i][0]]):
            raise self.retry()
    return result
