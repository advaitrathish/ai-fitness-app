from backend_sender import send_workout_to_backend
import cv2
import mediapipe as mp
import numpy as np
import time
import winsound
from collections import deque

# ================= CONFIG =================
TOTAL_TIME = 35
ANGLE_FLAT = 18
ANGLE_CRUNCH = 42
CONFIRM_FRAMES = 4

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

crunch_count = 0
stage = "down"
data_sent = False

angle_buffer = deque(maxlen=5)
up_frames = 0
down_frames = 0

# ================= HELPERS =================
def beep(freq=800, dur=120):
    try:
        winsound.Beep(freq, dur)
    except:
        pass

def calculate_torso_angle(shoulder, hip):
    shoulder = np.array(shoulder)
    hip = np.array(hip)

    radians = np.arctan2(
        abs(shoulder[1] - hip[1]),
        abs(shoulder[0] - hip[0])
    )

    angle = np.abs(radians * 180.0 / np.pi)
    return angle

def get_grade(count):
    if count >= 25:
        return "GOOD"
    elif count >= 12:
        return "AVERAGE"
    return "BAD"

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

    # ================= TIMER =================
    if timer_running:
        elapsed = int(current_time - start_time)
        remaining = max(0, TOTAL_TIME - elapsed)

        if remaining == 0:
            timer_running = False
            beep(1200, 500)

    skeleton_color = (255, 255, 255)  # default white

    # ================= CRUNCH DETECTION =================
    if results.pose_landmarks and timer_running:
        lm = results.pose_landmarks.landmark

        # Pick better visible side
        left_vis = lm[mp_pose.PoseLandmark.LEFT_HIP.value].visibility
        right_vis = lm[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility

        if left_vis > right_vis:
            shoulder = [
                lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
            ]
            hip = [
                lm[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                lm[mp_pose.PoseLandmark.LEFT_HIP.value].y
            ]
        else:
            shoulder = [
                lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
            ]
            hip = [
                lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y
            ]

        raw_angle = calculate_torso_angle(shoulder, hip)
        angle_buffer.append(raw_angle)
        smooth_angle = sum(angle_buffer) / len(angle_buffer)

        cv2.putText(frame, f"Angle: {int(smooth_angle)}",
                    (20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)

        # ---- Stable Stage Logic ----
        if smooth_angle < ANGLE_FLAT:
            down_frames += 1
            up_frames = 0

            if down_frames > CONFIRM_FRAMES:
                stage = "down"
                skeleton_color = (0, 0, 255)  # RED (flat)

        elif smooth_angle > ANGLE_CRUNCH:
            up_frames += 1
            down_frames = 0

            if up_frames > CONFIRM_FRAMES and stage == "down":
                stage = "up"
                crunch_count += 1
                skeleton_color = (0, 255, 0)  # GREEN (crunch)
                beep()
        else:
            up_frames = 0
            down_frames = 0

    # ================= RESULT =================
    if not timer_running and remaining == 0 and start_time != 0:
        grade = get_grade(crunch_count)

        if not data_sent:
            send_workout_to_backend(
                "crunches",
                crunch_count,
                TOTAL_TIME,
                grade
            )
            data_sent = True

        cv2.putText(frame, "WORKOUT OVER",
                    (100, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (255, 255, 255), 3)

        cv2.putText(frame, f"Crunches: {crunch_count}",
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

        cv2.putText(frame, f"Crunches: {crunch_count}",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0, 255, 0), 2)

    # ================= SKELETON DRAW =================
    if results.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=skeleton_color, thickness=3, circle_radius=4),
            mp_draw.DrawingSpec(color=skeleton_color, thickness=2, circle_radius=2)
        )

    cv2.imshow("AI Crunch Trainer", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('s'):
        crunch_count = 0
        remaining = TOTAL_TIME
        start_time = time.time()
        timer_running = True
        data_sent = False
        up_frames = 0
        down_frames = 0
        beep()

cap.release()
cv2.destroyAllWindows()