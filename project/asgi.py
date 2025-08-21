import os, django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import re_path
from supervisor.consummer import MQTTConsumer       # écoute MQTT
from supervisor.consumer_redis import FrontWSConsumer  # push front

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter([
        re_path(r"ws/mqtt/$", MQTTConsumer.as_asgi()),     
        re_path(r"ws/data/$", FrontWSConsumer.as_asgi()),  
    ])),
})

'''import os
import django
from channels.routing       import ProtocolTypeRouter, URLRouter
from django.core.asgi       import get_asgi_application
from django.urls            import path
from supervisor.consummer   import MQTTConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

#? Configurer Django
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
        path("ws/mqtt/", MQTTConsumer.as_asgi()),
    ]),
})
'''