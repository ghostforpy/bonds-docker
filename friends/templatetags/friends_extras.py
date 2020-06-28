from django import template
from ..models import UserFriends, UserFriendsRequests
# from bonds.friends.models import UserFriends
# from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter(name='new_friends_count')
def cut(user):
    request_friends_to = user.friend_request_to.all()
    request_friends_new = request_friends_to.filter(new=True)
    request_friends_new_count = request_friends_new.count()
    result = request_friends_new_count\
        if request_friends_new_count != 0 else ''
    return result


@register.filter(name='is_friends')
def is_friends(request_user, user):
    return UserFriends.is_friend(request_user.friends, user.friends)


@register.filter(name='request_already_exist')
def request_already_exist(request_user, user):
    request = request_user.friend_request_from.filter(user_to=user)
    return request.exists()


@register.filter(name='request_friends_id')
def request_friends_id(request_user, user):
    request = request_user.friend_request_from.filter(user_to=user)
    return request.get().id
