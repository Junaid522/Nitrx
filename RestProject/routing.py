from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
from django.urls import path

from RestProject.channels_middleware import TokenAuthMiddleware
from chat_app.consumers import ChatConsumer

application = ProtocolTypeRouter({
    "websocket": TokenAuthMiddleware(
        URLRouter([
            path('ws/', ChatConsumer.as_asgi())
        ]
        )
    ),
})
