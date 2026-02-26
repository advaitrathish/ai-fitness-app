from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import WorkoutSession, UserProfile
from .serializers import RegisterSerializer, MeSerializer
from rest_framework.views import APIView
from rest_framework import generics


# ============================
# REGISTER (CLASS BASED)
# ============================

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# ============================
# GET CURRENT USER PROFILE
# ============================

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user.profile)
        return Response(serializer.data)


# ============================
# LOG WORKOUT
# ============================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_workout(request):
    user = request.user
    data = request.data

    exercise_name = data.get('exercise_name')
    reps = int(data.get('reps', 0))
    duration = int(data.get('duration_minutes', 0))

    xp_earned = reps * 2 + duration * 5

    WorkoutSession.objects.create(
        user=user,
        exercise_name=exercise_name,
        reps=reps,
        duration_minutes=duration,
        xp_earned=xp_earned
    )

    profile = user.profile
    profile.xp += xp_earned
    profile.total_workouts += 1
    profile.recalculate_level()

    return Response({
        "xp_earned": xp_earned,
        "total_xp": profile.xp,
        "level": profile.level
    })


# ============================
# LEADERBOARD
# ============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    profiles = UserProfile.objects.select_related('user').order_by('-xp')[:10]

    data = [
        {
            "username": profile.user.username,
            "xp": profile.xp,
            "level": profile.level
        }
        for profile in profiles
    ]

    return Response(data)