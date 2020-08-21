from .models import InvestmentPortfolio

from config import celery_app
from django.utils.timezone import now
from django.core.mail import send_mail


@celery_app.task(bind=True,
                 name='portfolio.refresh_portfolio_changes',
                 default_retry_delay=30 * 60,
                 max_retries=6)
def refresh_portfolio_changes(self):
    portfolios = InvestmentPortfolio.objects.all()
    for i in portfolios:
        i.refresh_portfolio_changes()
