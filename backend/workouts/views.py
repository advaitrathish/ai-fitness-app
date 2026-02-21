import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Workout


@csrf_exempt
def save_workout(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST method allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)

        # Required fields
        user_id = data.get("user")
        exercise_name = data.get("exercise")
        rep_count = data.get("count")
        duration_value = data.get("duration")
        grade_value = data.get("grade")

        # Validate missing fields
        if not all([user_id, exercise_name, rep_count, duration_value, grade_value]):
            return JsonResponse(
                {"error": "Missing required fields"},
                status=400
            )

        # Validate user exists
        try:
            user_obj = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "Invalid user ID"},
                status=404
            )

        # Create workout
        workout = Workout.objects.create(
            user=user_obj,
            exercise=exercise_name,
            count=int(rep_count),
            duration=int(duration_value),
            grade=grade_value
        )

        return JsonResponse({
            "status": "success",
            "workout_id": workout.id,
            "exercise": workout.exercise,
            "count": workout.count,
            "duration": workout.duration,
            "grade": workout.grade,
            "date": workout.created_at.strftime("%Y-%m-%d"),
            "time": workout.created_at.strftime("%H:%M:%S")
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON format"},
            status=400
        )

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500
        )