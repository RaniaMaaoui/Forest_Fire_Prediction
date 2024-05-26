from django.shortcuts                   import render, redirect, get_object_or_404
from django.contrib.auth.decorators     import login_required
from django.http                        import JsonResponse

from authentication.decorators          import client_required
from supervisor.models.data             import Data
from .forms                             import SelectProjectForm
from supervisor.models.project          import Project
from supervisor.models.parcelle         import Parcelle
from supervisor.models.node             import Node
from django.db.models.functions         import TruncHour
from django.utils                       import timezone
import datetime
import json


# @login_required(login_url='client_login')
# @client_required
# def index1(request, project_id):
#     project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
#     return render(request, 'website/index1.html', {'project': project})


# @login_required(login_url='client_login')
# @client_required
# def node_list(request, project_id):
#     project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
#     return render(request, 'website/node_list.html', {'project': project})


# @login_required(login_url='client_login')
# @client_required
# def node_detail(request, project_id, node_id):
#     project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
#     node = get_object_or_404(Node, id=node_id, parcelle__project=project)
    
#     # Filtrer les données pour les dernières 24 heures
#     now = timezone.now()
#     start_of_period = now - datetime.timedelta(days=1)

#     data_entries = Data.objects.filter(node=node, published_date__range=(start_of_period, now))
    
#     # Créer un dictionnaire pour stocker les valeurs de température, humidité et gaz par intervalles de 1 heure
#     temperature_dict = {}
#     humidity_dict = {}
#     gas_dict = {}
    
#     for entry in data_entries:
#         interval = entry.published_date.replace(minute=0, second=0, microsecond=0)  # Truncating to the nearest hour
#         if interval not in temperature_dict:
#             temperature_dict[interval] = []
#         if interval not in humidity_dict:
#             humidity_dict[interval] = []
#         if interval not in gas_dict:
#             gas_dict[interval] = []
        
#         temperature_dict[interval].append(entry.temperature)
#         humidity_dict[interval].append(entry.humidity)
#         gas_dict[interval].append(entry.gaz)
    
#     # Calculer les valeurs moyennes pour chaque intervalle de 1 heure
#     temperatures = [{'interval': interval.isoformat(), 'temperature': sum(values)/len(values)} for interval, values in temperature_dict.items()]
#     humidity = [{'interval': interval.isoformat(), 'humidity': sum(values)/len(values)} for interval, values in humidity_dict.items()]
#     gas = [{'interval': interval.isoformat(), 'gas': sum(values)/len(values)} for interval, values in gas_dict.items()]
    
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         return JsonResponse({
#             'temperatures': temperatures,
#             'humidity': humidity,
#             'gas': gas
#         })

#     context = {
#         'project': project,
#         'node': node,
#         'temperatures': temperatures,
#         'humidity': humidity,
#         'gas': gas,
#     }

#     return render(request, 'website/node_detail.html', context)




# @login_required(login_url='client_login')
# @client_required
# def select_client_of_project(request):
#     client = request.user.client  
#     if request.method == 'POST':
#         form = SelectProjectForm(request.POST, client=client)
#         if form.is_valid():
#             project_id = form.cleaned_data['project'].polygon_id
#             return redirect('dashboard_client', project_id=project_id)
#     else:
#         form = SelectProjectForm(client=client)
    
#     return render(request, 'website/select_project.html', {'form': form})


# @login_required(login_url='client_login')
# @client_required
# def fetch_parcelles_for_project(request):
#     project_id = request.GET.get('project_id')
#     if not project_id:
#         return JsonResponse({'error': 'No project ID provided.'}, status=400)

#     project = get_object_or_404(Project, polygon_id=project_id, client=request.user.client)
#     parcelles = Parcelle.objects.filter(project=project)
#     parcelle_data = []
#     all_nodes = []

#     for parcelle in parcelles:
#         nodes = Node.objects.filter(parcelle=parcelle)
#         node_data = [{
#             'id': node.id,
#             'name': node.name,
#             'latitude': node.position.x,  
#             'longitude': node.position.y, 
#             'ref': node.reference, 
#             'last_data': get_last_data(node)
#         } for node in nodes]
        
#         all_nodes.extend(node_data)

#         parcelle_data.append({
#             'id': parcelle.id,
#             'name': parcelle.name,
#             'coordinates': list(parcelle.polygon.coords[0]),
#             'nodes': node_data
#         })
#     city_data = {
#         'localite_libelle': project.city.localite_libelle,
#         'latitude': project.city.latitude,
#         'longitude': project.city.longitude
#     }
    

#     return JsonResponse({
#         'parcelles': parcelle_data,
#         'city': city_data,
#     })


@login_required(login_url='client_login')
@client_required
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
            'last_data': get_last_data(node)
        } for node in nodes]
        all_nodes.extend(node_data)

    #* Vérifiez que le JSON est bien formé et non vide
    json_data = json.dumps(all_nodes, default=str)
    if not json_data:
        json_data = '[]'  

    context = {
        'project': project,
        'nodes': all_nodes,
        'last_data': json_data
    }

    return render(request, 'website/node_list.html', context)

def get_last_data(node):
    try:
        last_data = Data.objects.filter(node=node).latest('published_date')
        return {
            'temperature': last_data.temperature,
            'humidity': last_data.humidity,
            'rssi': node.RSSI,
            'fwi': node.FWI,
            'prediction_result': node.detection,
            'pressure': last_data.pressur,
            'gaz': last_data.gaz,
            'wind_speed': last_data.wind,
            'rain_volume': last_data.rain,
        }
    except Data.DoesNotExist:
        return {}


