from django.http import HttpResponse
from django.shortcuts                   import render, redirect, get_object_or_404
from django.contrib.auth.decorators     import login_required
from django.contrib                     import messages
from authentication.decorators          import supervisor_required
from supervisor.forms                   import ClientForm
from client.models                      import Client
import json


@login_required(login_url='supervisor_login')
@supervisor_required
def list_clients(request):
    clients = Client.objects.all()
    form = ClientForm()
    clientId=request.GET.dict().get('update_client')
    # clientId = None
        # return render(request, 'website/clients/list_client.html', {'clients': clients, 'form': form, 'update_form_client': update_form_client})

    return render(request, 'website/clients/list_client.html', {'clients': clients, 'form': form})


@login_required(login_url='supervisor_login')
@supervisor_required
def add_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            client = form.save(commit=False)
            client.save()
            form.save_m2m()
            messages.success(request, 'Client added successfully.')
            return redirect('supervisor:list_client')
        else:
            messages.error(request, 'Please correct the errors below.')

    return redirect('supervisor:list_client')


@login_required(login_url='supervisor_login')
@supervisor_required
def update_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES, instance=client)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated successfully.')
            return redirect('supervisor:list_client')
        else:
            messages.error(request, 'Please correct the errors below.')
        return redirect('supervisor:list_client')
    else:
        form = ClientForm(instance=client)
        client = {
        'firstName': client.__dict__.get('firstName'),
        'lastName': client.__dict__.get('lastName'),
        'email': client.__dict__.get('email'),
        'phone': client.__dict__.get('phone'),
        'username': client.__dict__.get('username'),
        'image': client.image.url
        }
        print(client)
        return HttpResponse( json.dumps( client ) )


@login_required(login_url='supervisor_login')
@supervisor_required
def delete_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    messages.success(request, 'Client deleted successfully.')
    return redirect('supervisor:list_client')
