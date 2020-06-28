from django.db import models
from bonds.users.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse
# Create your models here.


class UserFriends(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='friends')
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    friends = models.ManyToManyField("self")

    def is_friend(self, friend):
        if friend in self.friends.all():
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.user.username})

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_friend(sender, instance, created, **kwargs):
    if created:
        UserFriends.objects.create(user=instance)


class UserFriendsRequests(models.Model):
    user_from = models.ForeignKey(User,
                                  related_name='friend_request_from',
                                  on_delete=models.CASCADE,)
    user_to = models.ForeignKey(User,
                                related_name='friend_request_to',
                                on_delete=models.CASCADE,)
    accept = models.BooleanField(default=False)
    reject = models.BooleanField(default=False)
    new = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True,
                                   db_index=True)

    class Meta:
        ordering = ['-new', '-created']

    def already_exist(self):
        try:
            friend_request = UserFriendsRequests.\
                objects.filter(Q(user_from=self.user_from,
                                 user_to=self.user_to) |
                               Q(user_from=self.user_to,
                                 user_to=self.user_from))
            friend_request = friend_request.get()
            # return friend_request.id
            return True
        except ObjectDoesNotExist:
            return False
#        except MultipleObjectsReturned:
#            return 'Multiple'

    def save(self, *args, **kwargs):
        if self.user_to.friends.is_friend(self.user_from.friends):
            return 'already friends'
        if self.accept:
            user_to = UserFriends.objects.get(user=self.user_to)
            user_from = UserFriends.objects.get(user=self.user_from)
            user_to.friends.add(user_from)
            super(UserFriendsRequests, self).delete(*args, **kwargs)
            return 'friend_added'
        else:
            if self.reject:
                super(UserFriendsRequests, self).delete(*args, **kwargs)
                return 'request_deleted'
            else:
#                if self.already_exist():
#                    return 'already_exist'
                super(UserFriendsRequests, self).save(*args, **kwargs)
                return 'request_saved'
