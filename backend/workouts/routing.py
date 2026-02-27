from django.urls import re_path
from .consumers import SquatConsumer

websocket_urlpatterns = [
    re_path(r"ws/squats/$", SquatConsumer.as_asgi()),
]