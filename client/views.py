from django.shortcuts                   import render, redirect, get_object_or_404
from django.contrib.auth.decorators     import login_required
from django.http                        import JsonResponse
from .forms                             import SelectProjectForm
from supervisor.models.project          import Project
from supervisor.models.parcelle         import Parcelle
from supervisor.models.node             import Node
import json


@login_required(login_url='client_login')
def index1(request, project_id):
    project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
    return render(request, 'website/index1.html', {'project': project})



@login_required(login_url='client_login')
def node_list(request, project_id):
    project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
    return render(request, 'website/node_list.html', {'project': project})



@login_required(login_url='client_login')
def node_detail(request, project_id, node_id):
    project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
    node = get_object_or_404(Node, id=node_id, parcelle__project=project)
    return render(request, 'website/node_detail.html', {'project': project, 'node': node})



@login_required(login_url='client_login')
def select_client_of_project(request):
    client = request.user.client  
    if request.method == 'POST':
        form = SelectProjectForm(request.POST, client=client)
        if form.is_valid():
            project_id = form.cleaned_data['project'].polygon_id
            return redirect('dashboard_client', project_id=project_id)
    else:
        form = SelectProjectForm(client=client)
    
    return render(request, 'website/select_project.html', {'form': form})


@login_required(login_url='client_login')
def fetch_parcelles_for_project(request):
    project_id = request.GET.get('project_id')
    if not project_id:
        return JsonResponse({'error': 'No project ID provided.'}, status=400)

    project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
    parcelles = Parcelle.objects.filter(project=project)
    parcelle_data = []
    all_nodes = []

    for parcelle in parcelles:
        nodes = Node.objects.filter(parcelle=parcelle)
        node_data = [{
            'id': node.id,
            'name': node.name,
            'latitude': node.position.x,  
            'longitude': node.position.y, 
            'ref': node.reference, 
        } for node in nodes]
        
        all_nodes.extend(node_data)

        parcelle_data.append({
            'id': parcelle.id,
            'name': parcelle.name,
            'coordinates': list(parcelle.polygon.coords[0]),
            'nodes': node_data
        })
    city_data = {
        'localite_libelle': project.city.localite_libelle,
        'latitude': project.city.latitude,
        'longitude': project.city.longitude
    }
    

    return JsonResponse({
        'parcelles': parcelle_data,
        'city': city_data,
    })







@login_required(login_url='client_login')
def node_list(request, project_id):
    project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
    parcelles = Parcelle.objects.filter(project=project)
    all_nodes = []

    for parcelle in parcelles:
        nodes = Node.objects.filter(parcelle=parcelle)
        node_data = [{
            'id': node.id,
            'name': node.name,
            'latitude': node.position.x,  
            'longitude': node.position.y, 
            'ref': node.reference, 
        } for node in nodes]
        all_nodes.extend(node_data)

    context = {
        'project': project,
        'nodes': all_nodes
    }

    return render(request, 'website/node_list.html', context)