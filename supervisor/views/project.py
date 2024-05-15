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
    ).values('full_name').annotate(count=Count('client')).order_by('full_name')

    if client_id:
        projects = Project.objects.filter(client_id=client_id)  # Filter projects by client ID
    else:
        projects = Project.objects.all()

    form = ProjectForm()
    return render(request, 'website/project.html', {
        'projects_by_client': projects_by_client,
        'projects': projects,
        'form': form
    })



@login_required(login_url='supervisor_login')
def add_project(request):
    form = ProjectForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m()
            messages.success(request, 'Project added successfully.')
            request.session['project_added'] = True  #* Set session variable
            return redirect(reverse('supervisor:add_project'))  #* Redirection après succès
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()
    show_map_modal = request.session.get('project_added', False)  #* Read without removing
    return render(request, 'website/project.html', {'form': form, 'show_map_modal': show_map_modal})






@login_required(login_url='supervisor_login')
def update_project(request):
    pass



@login_required(login_url='supervisor_login')
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'Project deleted successfully.')
    return redirect('supervisor:list_project')