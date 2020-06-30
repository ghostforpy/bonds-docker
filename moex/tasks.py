from .models import Security

from config import celery_app
from django.utils.timezone import now


@celery_app.task(name='moex.refresh_security')
def refresh_security():
    today = now().date()
    if today.weekday() not in [7, 1]:
        securities = Security.objects.filter(last_update__lt=today)
        for security in securities:
            security.refresh_price()
