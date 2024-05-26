from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from authentication.decorators      import supervisor_required



@login_required(login_url='supervisor_login')
@supervisor_required
def index(request):
    return render(request, 'website/index.html', {})