from django.http                    import JsonResponse
from django.shortcuts               import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from supervisor.forms               import NodeForm, ParcelleForm, ProjectForm
from supervisor.models.project      import Project
from supervisor.models.parcelle     import Parcelle 
from django.contrib                 import messages
from django.db.models               import Count, Value
from django.db.models.functions     import Concat
from django.contrib.gis.geos        import Polygon
from supervisor.models.node         import Node
from django.contrib.gis.geos        import Point
import json

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

@login_required(login_url='supervisor_login')
def add_project(request):
    form = ProjectForm(request.POST or None, request.FILES or None)
    data = {'latitude': None, 'longitude': None}
    client_name = None
    project_name = None

    if request.method == 'POST':
        if form.is_valid():
            project = form.save(commit=False)
            project_name = project.name
            client_name = f"{project.client.firstName} {project.client.lastName}"

            # Vérifiez si un projet avec le même nom et la même ville existe déjà
            existing_project = Project.objects.filter(name=project_name, city=project.city).first()

            if existing_project:
                existing_project.descp = form.cleaned_data.get('descp', existing_project.descp)
                existing_project.date_debut = form.cleaned_data.get('date_debut', existing_project.date_debut)
                existing_project.date_fin = form.cleaned_data.get('date_fin', existing_project.date_fin)
                existing_project.client = form.cleaned_data.get('client', existing_project.client)
                existing_project.save()
                messages.success(request, 'Project updated successfully.')
                project = existing_project
            else:
                project.save()
                form.save_m2m()
                messages.success(request, 'Project added successfully.')
            
            latitude = float(project.city.latitude)
            longitude = float(project.city.longitude)
            data = {'latitude': latitude, 'longitude': longitude}
            request.session['project_added'] = True  
            request.session['map_data'] = data
            parcelle_form = ParcelleForm(initial={'project': project})
            node_form = NodeForm()
            return render(request, 'website/project.html', {
                'form': form,
                'show_map_modal': True,
                'data': data,
                'parcelle_form': parcelle_form,
                'node_form': node_form,
                'project_name': project_name,
                'client_name': client_name
            })
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm()

    if 'map_data' in request.session:
        data = request.session['map_data']

    show_map_modal = request.session.get('project_added', False)
    response = render(request, 'website/project.html', {
        'form': form,
        'show_map_modal': show_map_modal,
        'data': data,
        'project_name': project_name,
        'client_name': client_name
    })

    request.session['project_added'] = False
    request.session['map_data'] = None

    return response


@login_required(login_url='supervisor_login')
def get_project_details(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
        data = {
            'project_name': project.name,
            'client_name': f"{project.client.firstName} {project.client.lastName}",
        }
        return JsonResponse(data)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

@login_required(login_url='supervisor_login')
def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('supervisor:list_project')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'website/project.html', {
        'form': form,
        'update': True,
        'project': project,
    })


@login_required(login_url='supervisor_login')
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'Project deleted successfully.')
    return redirect('supervisor:list_project')

@login_required(login_url='supervisor_login')
def parcelle_create(request):
    if request.method == 'POST':
        form = ParcelleForm(request.POST)
        if form.is_valid():
            coordinates_data = request.POST.get('coordinates')
            parcelle_id = request.POST.get('parcelle_id', None)
            try:
                coordinates = json.loads(coordinates_data)
                if coordinates[0] != coordinates[-1]:
                    coordinates.append(coordinates[0])
                polygon = Polygon(coordinates)

                if parcelle_id:
                    parcelle = get_object_or_404(Parcelle, id=parcelle_id)
                    parcelle.polygon = polygon
                    parcelle.save()
                    message = 'Polygon updated successfully.'
                else:
                    existing_parcelles = Parcelle.objects.all()
                    for existing_parcelle in existing_parcelles:
                        if polygon.equals_exact(existing_parcelle.polygon, tolerance=1e-9):
                            return JsonResponse({'error': {'name': [{'message': 'A parcel with these coordinates already exists.', 'code': 'unique'}]}}, status=400)

                    parcelle = form.save(commit=False)
                    parcelle.polygon = polygon
                    parcelle.save()
                    message = 'Polygon added successfully.'

                parcels = [{
                    'id': p.id,
                    'name': p.name,
                    'coordinates': list(p.polygon.coords[0])
                } for p in Parcelle.objects.filter(project=parcelle.project)]

                return JsonResponse({'message': message, 'parcels': parcels}, status=200)
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': {'coordinates': [{'message': 'Invalid coordinates format.', 'code': 'invalid'}]}}, status=400)
        else:
            errors = form.errors.get_json_data()
            return JsonResponse({'error': errors}, status=400)
    else:
        form = ParcelleForm()
        projects = Project.objects.all()
        project_data = []

        for project in projects:
            parcelles = Parcelle.objects.filter(project=project)
            project_parcelles = [{
                'id': parcelle.id,
                'name': parcelle.name,
                'coordinates': list(parcelle.polygon.coords[0])
            } for parcelle in parcelles]
            project_data.append({
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'latitude': project.city.latitude,
                    'longitude': project.city.longitude
                },
                'parcelles': project_parcelles
            })

        return render(request, 'website/project.html', {
            'form': form,
            'project_data': project_data, 
        })



@login_required(login_url='supervisor_login')
def get_parcelles_for_project(request):
    project_id = request.GET.get('project_id')
    if project_id:
        parcelles = Parcelle.objects.filter(project_id=project_id)
        parcelle_data = [{
            'id': parcelle.id,
            'name': parcelle.name,
            'coordinates': list(parcelle.polygon.coords[0])
        } for parcelle in parcelles]
        return JsonResponse({'parcelles': parcelle_data}, status=200)
    else:
        return JsonResponse({'error': 'No project ID provided.'}, status=400)
    


@login_required(login_url='supervisor_login')
def node_create(request):
    if request.method == 'POST':
        node_form = NodeForm(request.POST)
        # print(request.POST)  # Affiche les données POST reçues

        if node_form.is_valid():
            print('hello')  
            coordinates_data = request.POST.get('position')
            parcelle_id = request.POST.get('parcelle')
            try:
                # Extraire les coordonnées du point
                coordinates = coordinates_data.strip('POINT()').split()
                longitude = float(coordinates[0])
                latitude = float(coordinates[1])
                point = Point(latitude, longitude)

                parcelle = get_object_or_404(Parcelle, id=parcelle_id)

                # Vérifier si le point est à l'intérieur du polygone de la parcelle
                if parcelle.polygon.contains(point):
                    node = node_form.save(commit=False)
                    node.position = point
                    node.latitude = latitude
                    node.longitude = longitude
                    node.parcelle = parcelle
                    node.save()
                    message = 'Node added successfully.'
                    
                    nodes = [{
                        'id': n.id,
                        'name': n.name,
                        'coordinates': [n.position.x, n.position.y]
                    } for n in Node.objects.filter(parcelle=node.parcelle)]
                    
                    return JsonResponse({'message': message, 'nodes': nodes}, status=200)
                else:
                    return JsonResponse({'error': {'_all__': 'The node must be placed inside the plot.'}}, status=400)
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': {'coordinates': [{'message': 'Invalid coordinates format.', 'code': 'invalid'}]}}, status=400)
        else:
            # Afficher les erreurs de validation du formulaire
            errors = node_form.errors.as_json()
            print('Form errors:', errors)  # Debug: Affiche les erreurs du formulaire
            return JsonResponse({'error': errors}, status=400)
    else:
        node_form = NodeForm()
        return render(request, 'website/project.html', {'node_form': node_form})
    


@login_required(login_url='supervisor_login')
def get_parcelles_with_nodes_for_project(request):
    project_id = request.GET.get('project_id')
    if project_id:
        parcelles = Parcelle.objects.filter(project_id=project_id)
        parcelle_data = []
        for parcelle in parcelles:
            nodes = Node.objects.filter(parcelle=parcelle)
            node_data = [{
                'id': node.id,
                'name': node.name,
                'latitude': node.position.x,
                'longitude': node.position.y,
                'ref': node.reference
            } for node in nodes]
            parcelle_data.append({
                'id': parcelle.id,
                'name': parcelle.name,
                'coordinates': list(parcelle.polygon.coords[0]),
                'nodes': node_data
            })
        return JsonResponse({'parcelles': parcelle_data}, status=200)
    else:
        return JsonResponse({'error': 'No project ID provided.'}, status=400)
