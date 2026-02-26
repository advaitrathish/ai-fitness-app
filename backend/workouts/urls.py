from django.urls import path
from .views import RegisterView, MeView, log_workout, leaderboard

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("log-workout/", log_workout),
    path("leaderboard/", leaderboard),
]