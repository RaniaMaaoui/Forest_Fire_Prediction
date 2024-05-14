from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import SupervisorLoginForm
from supervisor.models.supervisor import Supervisor

def client(request):
    return render(request, 'website/client.html')

def supervisor_login(request):
    if request.method == 'POST':
        form = SupervisorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            supervisor = Supervisor.objects.get(email=email)
            login(request, supervisor.user)
            next_url = request.POST.get('next', 'supervisor:dashboard_super')
            return redirect(next_url)
        return render(request, 'website/supervisor.html', {'form': form})
    form = SupervisorLoginForm()
    return render(request, 'website/supervisor.html', {'form': form})

def sign_out(request):
    """Log out the current user."""
    logout(request)
    return redirect('supervisor_login')
