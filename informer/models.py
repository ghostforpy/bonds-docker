from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.


class UserInformer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='informer',
        verbose_name='informer'
    )
    enable = models.BooleanField(
        default=True
    )
