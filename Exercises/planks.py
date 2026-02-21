from backend_sender import send_workout_to_backend
import cv2
import mediapipe as mp
import numpy as np
import time
import winsound

# ================= CONFIG =================
TOTAL_TIME = 35
ANGLE_MIN = 165
ANGLE_MAX = 195
IDLE_LIMIT = 5

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

# ================= STATE =================
timer_running = False
start_time = 0
remaining = TOTAL_TIME

total_hold_time = 0.0
data_sent = False
form_good = False
last_timestamp = time.time()
last_good_time = time.time()

# ================= HELPERS =================
def beep(freq=900, dur=120):
    try:
        winsound.Beep(freq, dur)
    except:
        pass

def get_grade(seconds):
    if seconds >= 25:
        return "GOOD"
    elif seconds >= 15:
        return "AVERAGE"
    return "BAD"

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

# ================= MAIN LOOP =================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    current_time = time.time()
    dt = current_time - last_timestamp
    last_timestamp = current_time

    # ================= TIMER =================
    if timer_running:
        elapsed = int(current_time - start_time)
        remaining = max(0, TOTAL_TIME - elapsed)

        if remaining == 0:
            timer_running = False
            beep(1200, 400)

    skeleton_color = (255, 255, 255)

    # ================= PLANK LOGIC =================
    if results.pose_landmarks and timer_running:
        lm = results.pose_landmarks.landmark

        # Pick clearer side
        left_vis = lm[mp_pose.PoseLandmark.LEFT_HIP.value].visibility
        right_vis = lm[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility

        if left_vis > right_vis:
            shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            hip = lm[mp_pose.PoseLandmark.LEFT_HIP.value]
            ankle = lm[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        else:
            shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            hip = lm[mp_pose.PoseLandmark.RIGHT_HIP.value]
            ankle = lm[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

        if hip.visibility > 0.6:
            angle = calculate_angle(
                [shoulder.x, shoulder.y],
                [hip.x, hip.y],
                [ankle.x, ankle.y]
            )

            is_horizontal = abs(shoulder.x - ankle.x) > abs(shoulder.y - ankle.y)

            if is_horizontal and ANGLE_MIN < angle < ANGLE_MAX:
                form_good = True
                total_hold_time += dt
                last_good_time = current_time
                skeleton_color = (0, 255, 0)  # Green = correct
            else:
                form_good = False
                skeleton_color = (0, 0, 255)  # Red = wrong form

            cv2.putText(frame, f"Hip Angle: {int(angle)}",
                        (20, 170),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 2)

        # Idle detection
        if current_time - last_good_time > IDLE_LIMIT:
            cv2.putText(frame, "FIX FORM!",
                        (20, 200),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 165, 255), 2)

    # ================= RESULT =================
    if not timer_running and remaining == 0 and start_time != 0:
        grade = get_grade(total_hold_time)

        if not data_sent:
            send_workout_to_backend(
                "planks",
                int(total_hold_time),
                TOTAL_TIME,
                grade
            )
            data_sent = True

        cv2.putText(frame, "WORKOUT OVER",
                    (100, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (255, 255, 255), 3)

        cv2.putText(frame, f"Held: {int(total_hold_time)}s",
                    (100, 200),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 255, 0), 3)

        cv2.putText(frame, f"Grade: {grade}",
                    (100, 250),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 255, 255), 3)

    else:
        cv2.rectangle(frame, (0, 0), (350, 120), (0, 0, 0), -1)

        cv2.putText(frame, f"Time: {remaining}s",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (0, 255, 255), 2)

        hold_color = (0, 255, 0) if form_good else (255, 255, 255)

        cv2.putText(frame, f"Held: {int(total_hold_time)}s",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, hold_color, 2)

    # ================= SKELETON =================
    if results.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=skeleton_color, thickness=3, circle_radius=4),
            mp_draw.DrawingSpec(color=skeleton_color, thickness=2, circle_radius=2)
        )

    cv2.imshow("AI Plank Trainer", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('s'):
        total_hold_time = 0
        remaining = TOTAL_TIME
        start_time = time.time()
        last_timestamp = time.time()
        last_good_time = time.time()
        timer_running = True
        data_sent = False
        beep()

cap.release()
cv2.destroyAllWindows()