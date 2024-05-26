import os
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
