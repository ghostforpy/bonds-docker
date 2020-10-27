from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def create_user_informer(sender, instance, created, **kwargs):
    if created:
        UserInformer.objects.create(user=instance)
