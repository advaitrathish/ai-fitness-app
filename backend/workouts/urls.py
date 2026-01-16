from django.urls import path
from .views import save_squat_workout

urlpatterns = [
    path("api/workout/squat/", save_squat_workout),
]
