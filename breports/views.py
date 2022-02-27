from django.shortcuts import render
import os
# Create your views here.


def main(request):
    mode = os.environ['DJANGO_SETTINGS_MODULE']
    mode = mode.split('.')[-1]
    return render(request,
                  'breports/main_with_vue.html',
                  {'mode': mode})
