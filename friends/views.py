from django.shortcuts import render  # , get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import UserFriendsRequests
from bonds.users.models import User
from django.db.models import Q

# Create your views here.


@login_required
def friends_list(request):
    friends = request.user.friends.friends.all()
    request_friends_from = request.user.friend_request_from.all()
    request_friends_to = list(request.user.friend_request_to.all())
    request.user.friend_request_to.all().update(new=False)
    return render(request,
                  'friends/list.html',
                  {'friends': friends,
                   'request_friends_to': request_friends_to,
                   'request_friends_from': request_friends_from,
                   'user': request.user,
                   })


@require_POST
@login_required
def friends_delete(request, id):
    try:
        user_friend = User.objects.get(id=id)
        url = reverse('friends:friends_send_request',
                      args=[user_friend.id])
        request.user.friends.friends.remove(user_friend.friends)
        return JsonResponse({'status': 'friend_deleted', 'url': url})
    except ValueError:
        return JsonResponse({'status': 'no_user_in_friends'})
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_friend_id'})


@require_POST
@login_required
def friends_request_accept(request, id):
    try:
        friends_request = UserFriendsRequests.objects.get(id=id)
        if friends_request.user_to == request.user:
            friends_request.accept = True
            url = reverse('friends:friends_delete',
                          args=[friends_request.user_from.id])
            status = friends_request.save()
            return JsonResponse({'status': status, 'url': url})
        else:
            return JsonResponse({'status': 'no_valid'})
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_friend_request_id'})


@require_POST
@login_required
def friends_request_reject(request, id):
    try:
        friends_request = UserFriendsRequests.objects.get(id=id)
        if friends_request.user_to == request.user:
            friends_request.reject = True
            url = reverse('friends:friends_send_request',
                          args=[friends_request.user_from.id])
            status = friends_request.save()
            return JsonResponse({'status': status, 'url': url})
        else:
            return JsonResponse({'status': 'no_valid'})
    except ObjectDoesNotExist:
        print('1')
        return JsonResponse({'status': 'no_friend_request_id'})


@require_POST
@login_required
def friends_request_cancel(request, id):
    try:
        friends_request = UserFriendsRequests.objects.get(id=id)
        if friends_request.user_from == request.user:
            url = reverse('friends:friends_send_request',
                          args=[friends_request.user_to.id])
            friends_request.delete()
            return JsonResponse({'status': 'request_canceled', 'url': url})
        else:
            return JsonResponse({'status': 'no_valid'})
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_friend_request_id'})


@require_POST
@login_required
def friends_send_request(request, id):
    try:
        user = User.objects.get(id=id)
        try:
            friend_request = UserFriendsRequests.\
                objects.filter(Q(user_from=request.user,
                                 user_to=user) |
                               Q(user_from=user,
                                 user_to=request.user))
            friend_request = friend_request.get()
            content = {'status': 'already_exist'}
            content['url_accept'] = reverse('friends:friends_request_accept',
                                            args=[friend_request.id])
            content['url_reject'] = reverse('friends:friends_request_reject',
                                            args=[friend_request.id])
        except ObjectDoesNotExist:
            new_friend_request = UserFriendsRequests.objects.create(
                user_from=request.user, user_to=user)
            status = new_friend_request.save()
            content = {'status': status}
            if status == 'request_saved':
                content['url'] = reverse('friends:friends_request_cancel',
                                         args=[new_friend_request.id])
        return JsonResponse(content)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_user_id'})
