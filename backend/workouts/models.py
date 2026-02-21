from django.db import models
from django.contrib.auth.models import User


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.CharField(max_length=100)

    # Temporarily allow NULL so migration succeeds
    count = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)

    grade = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise}"