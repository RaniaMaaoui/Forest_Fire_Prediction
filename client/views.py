from django.shortcuts               import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='client_login')
def index1(request):
    return render(request, 'website/index1.html', {})


@login_required(login_url='client_login')
def node_list(request):
    return render(request, 'website/node_list.html', {})


@login_required(login_url='client_login')
def node_detail(request):
    return render(request, 'website/node_detail.html', {})

