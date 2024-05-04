from django.urls import path
from . import views


app_name = 'supervisor'

urlpatterns = [
    path('', views.index, name='dashboard_super'),
    path('list_client/', views.list_clients, name="list_client"),
    path('add_client/', views.add_client, name="add_client"),
    path('update_client/<int:pk>/', views.update_client, name="update_client"),
    path('delete_client/<int:pk>/', views.delete_client, name="delete_client"),
    path('project_list/', views.project, name='project'),
    path('noeuds_list/', views.noeuds, name='noeuds'),
    path('chart_super/', views.chart, name='chart_super')
]


