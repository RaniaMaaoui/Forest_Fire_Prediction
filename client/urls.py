from django.urls    import path
from .              import views

urlpatterns = [
    path('', views.index1, name='dashboard_client'),
    path('node_detail/', views.node_detail, name='node_detail'),
    path('node_list/', views.node_list, name='node_list'),
]