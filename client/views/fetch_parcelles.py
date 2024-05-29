from django.shortcuts                   import get_object_or_404
from django.contrib.auth.decorators     import login_required
from django.http                        import JsonResponse
from authentication.decorators          import client_required
from supervisor.models.data             import Data
from supervisor.models.project          import Project
from supervisor.models.parcelle         import Parcelle
from supervisor.models.node             import Node



@login_required(login_url='client_login')
@client_required
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
            'last_data': get_last_data(node)
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