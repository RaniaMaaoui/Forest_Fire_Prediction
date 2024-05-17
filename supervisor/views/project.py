from django.shortcuts               import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from supervisor.forms               import ProjectForm
from supervisor.models.project      import Project
from django.contrib                 import messages
from django.db.models               import Count, Value
from django.db.models.functions     import Concat
from django.urls import reverse



@login_required(login_url='supervisor_login')
def list_project(request):
    client_id = request.GET.get('client_id')
    projects_by_client = Project.objects.annotate(
        full_name=Concat('client__firstName', Value(' '), 'client__lastName')
    ).values('full_name', 'client_id').annotate(count=Count('client')).order_by('full_name')
    if client_id:
        projects = Project.objects.filter(client_id=client_id)  
    else:
        projects = Project.objects.all()
    form = ProjectForm()
    return render(request, 'website/project.html', {
        'projects_by_client': projects_by_client,
        'projects': projects,
        'form': form
    })



def add_project(request):
    form = ProjectForm(request.POST or None, request.FILES or None)
    data = {'latitude': None, 'longitude': None}

    if request.method == 'POST':
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m()
            messages.success(request, 'Project added successfully.')
            latitude = float(project.city.latitude)
            longitude = float(project.city.longitude)
            data = {'latitude': latitude, 'longitude': longitude}
            request.session['project_added'] = True  #* Set session variable
            request.session['map_data'] = data 
            form = ProjectForm()
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()

    #? Charger les données de la session si elles existent
    if 'map_data' in request.session:
        data = request.session['map_data']

    show_map_modal = request.session.get('project_added', False)  #* Read without removing
    response = render(request, 'website/project.html', {'form': form, 'show_map_modal': show_map_modal, 'data': data})

    #! Reset session variables after rendering the response
    request.session['project_added'] = False
    request.session['map_data'] = None

    return response


@login_required(login_url='supervisor_login')
def update_project(request):
    pass



@login_required(login_url='supervisor_login')
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'Project deleted successfully.')
    return redirect('supervisor:list_project')