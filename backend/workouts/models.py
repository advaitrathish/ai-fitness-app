from django.db import models

class Workout(models.Model):
    exercise = models.CharField(max_length=50)
    count = models.IntegerField()
    duration = models.IntegerField()  # seconds
    grade = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exercise} - {self.count}"
