from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/broker_reports/user_<id>/<filename>
    return 'broker_reports/user_{0}/{1}'.format(instance.owner.id, filename)


class BReport(models.Model):
    # model for upload broker reports
    owner = models.ForeignKey(
        User,
        related_name='breports',
        verbose_name='owner',
        on_delete=models.CASCADE
    )
    filename = models.FileField(upload_to=user_directory_path)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.filename)
