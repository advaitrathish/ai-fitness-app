import requests

# 👇 Set your current logged-in user ID here
# (Later we will automate this properly)
USER_ID = 1

def send_workout_to_backend(exercise_name, count, duration, grade):
    print("\n===== SENDING DATA TO BACKEND =====")

    url = "http://127.0.0.1:8000/api/workout/"

    payload = {
        "user": USER_ID,
        "exercise": exercise_name,
        "count": count,
        "duration": duration,
        "grade": grade
    }

    try:
        response = requests.post(url, json=payload)

        print("Status Code:", response.status_code)
        print("Raw Response:", response.text)

        if response.text.strip():
            print("Parsed JSON:", response.json())

    except Exception as e:
        print("Backend exception:", e)