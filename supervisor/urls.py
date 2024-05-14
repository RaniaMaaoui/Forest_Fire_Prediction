from django.urls    import path
from .              import views


app_name = 'supervisor'

urlpatterns = [
    path('', views.index, name='dashboard_super'),
            ####### CRUD OF CLIENT  ##########
    path('list_client/', views.list_clients, name="list_client"),
    path('add_client/', views.add_client, name="add_client"),
    path('update_client/<int:pk>/', views.update_client, name="update_client"),
    path('delete_client/<int:pk>/', views.delete_client, name="delete_client"),

            ####### CRUD OF CLIENT  ##########
    path('project_list/', views.list_project, name='list_project'),
    path('projects/<int:client_id>/', views.list_project, name='client_projects'),
    path('add_project/', views.add_project, name= 'add_project'),
    path('update_project/<int:pk>', views.update_project, name='update_project'),
    path('delete_project/<int:pk>', views.delete_project, name='delete_project'),

    
    path('noeuds_list/', views.noeuds, name='noeuds'),
    path('chart_super/', views.chart, name='chart_super')
]


