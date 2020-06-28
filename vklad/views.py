from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .forms import FormVkladInvestHistory
from .models import UserVklad, VkladInvestHistory
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
# Create your views here.


def updated_vklad(vklad):
    return {'invest_cash': str(vklad.invest_cash),
            'today_cash': str(vklad.today_cash),
            'ostatok': str(vklad.ostatok),
            'percent_profit': str(vklad.percent_profit),
            'year_percent_profit': str(vklad.year_percent_profit),
            }


@login_required
def detail_vklad(request):
    user = request.user
    vklad = user.vklad
    form = FormVkladInvestHistory()
    return render(request,
                  'vklad/detail.html',
                  {'vklad': vklad,
                   'form': form,
                   'user': user})


@login_required
@require_POST
def add_vklad(request, id):
    form = FormVkladInvestHistory(data=request.POST)
    print(request.POST)
    if form.is_valid():
        try:
            vklad = get_object_or_404(UserVklad, id=id)
            if vklad.owner == request.user:
                new_item = form.save(commit=False)
                new_item.vklad = vklad
                status = new_item.save()
                content = {'status': status}
                if status == 'ok':
                    content.update({'id': str(new_item.id)})
                    content.update(updated_vklad(vklad))
                return JsonResponse(content)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'no_id'})
    return JsonResponse({'status': 'no_valid'})


@require_POST
@login_required
def del_vklad(request, id):
    try:
        vklad = get_object_or_404(VkladInvestHistory, id=id)
        if vklad.vklad.owner == request.user:
            status = vklad.delete()
            content = {'status': status}
            if status == 'ok':
                content.update(updated_vklad(vklad.vklad))
            return JsonResponse(content)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id'})


@login_required
def refresh_vklad(request, id):
    try:
        vklad = get_object_or_404(UserVklad, id=id)
        if vklad.owner == request.user:
            vklad.refresh_vklad()
            content = {'status': 'ok'}
            content.update(updated_vklad(vklad))
            return JsonResponse(content)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id'})
