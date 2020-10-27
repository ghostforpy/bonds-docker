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


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()
