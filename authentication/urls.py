from django.urls    import path
from .              import  views

urlpatterns = [

    path('client/', views.client_login, name='client_login'),
    path('logout/', views.sign_out_client, name='logout_client'),

    path('supervisor/',views.supervisor_login, name = "supervisor_login"),
    path('logout/', views.sign_out, name = 'sign_out'),
]