from django.urls import path
from .views import save_workout

urlpatterns = [
    path("api/workout/", save_workout),
]