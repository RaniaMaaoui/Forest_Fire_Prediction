from django.urls    import path
from .              import views

urlpatterns = [
    path('<int:project_id>/', views.index1, name='dashboard_client'),
    path('node_detail/<int:project_id>/<int:node_id>/', views.node_detail, name='node_detail'),
    path('node_list/<int:project_id>/', views.node_list, name='node_list'),
    path('select_project_of_client/', views.select_client_of_project, name='select_project_of_project'),
    path('fetch_parcelles_for_project/', views.fetch_parcelles_for_project, name = 'fetch_parcelles_for_project'),
]