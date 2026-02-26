from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ============================
# USER PROFILE (XP + LEVEL + FITNESS DATA)
# ============================

class UserProfile(models.Model):

    GOAL_CHOICES = [
        ("cut", "Cut"),
        ("bulk", "Bulk"),
        ("maintain", "Maintain"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Gamification
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    total_workouts = models.IntegerField(default=0)

    # Fitness onboarding data
    age = models.IntegerField(default=0)
    height = models.FloatField(default=0)  # cm
    weight = models.FloatField(default=0)  # kg
    goal = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES,
        default="maintain"
    )
    consent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Profile"

    def recalculate_level(self):
        """
        Simple leveling formula:
        Level up every 500 XP
        """
        self.level = (self.xp // 500) + 1
        self.save()


# ============================
# WORKOUT SESSION
# ============================

class WorkoutSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workouts'
    )
    exercise_name = models.CharField(max_length=100)
    reps = models.IntegerField()
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField(default=0)
    xp_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.exercise_name}"


# ============================
# ACHIEVEMENTS
# ============================

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    xp_required = models.IntegerField()

    def __str__(self):
        return self.name


# ============================
# USER ACHIEVEMENTS
# ============================

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} unlocked {self.achievement.name}"