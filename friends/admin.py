from django.contrib import admin
from .models import UserFriends, UserFriendsRequests
# Register your models here.


@admin.register(UserFriends)
class UserFriendsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created']
    list_filter = ('user', 'created')
    search_fields = ('user',)


@admin.register(UserFriendsRequests)
class UserFriendsRequests(admin.ModelAdmin):
    list_display = ['id', 'user_from', 'user_to', 'accept',
                    'reject', 'new', 'created']
    list_filter = ('user_from', 'user_to', 'accept', 'reject', 'new',)
    search_fields = ('user',)
