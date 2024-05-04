from django.urls    import path
from .              import  views

urlpatterns = [
    path('client/',views.client, name = "client"),
    path('supervisor/',views.supervisor_login, name = "supervisor_login"),
    path('logout/', views.sign_out, name = 'sign_out'),
]