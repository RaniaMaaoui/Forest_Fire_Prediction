from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='supervisor_login')
def noeuds(request):
    return render(request, 'website/noeuds.html', {})