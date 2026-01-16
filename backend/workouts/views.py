import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Workout

@csrf_exempt
def save_squat_workout(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)

        workout = Workout.objects.create(
            exercise="squats",
            count=data.get("count"),
            duration=data.get("duration"),
            grade=data.get("grade")
        )

        return JsonResponse({
            "status": "success",
            "id": workout.id
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
