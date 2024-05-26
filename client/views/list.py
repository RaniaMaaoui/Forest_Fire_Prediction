import json
from django.shortcuts                   import render, get_object_or_404
from django.contrib.auth.decorators     import login_required
from authentication.decorators          import client_required
from supervisor.models.data             import Data
from supervisor.models.node             import Node
from supervisor.models.parcelle         import Parcelle
from supervisor.models.project          import Project


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