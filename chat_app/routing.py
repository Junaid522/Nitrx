from django.conf.urls import url
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/', consumers.ChatConsumer),
    # url(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
