from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings

def homePage(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, settings.LOGIN_REDIRECT_URL))
    else:
        template = 'comparator/home.html'
        return render(request, template)