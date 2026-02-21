from backend_sender import send_workout_to_backend
import cv2
import mediapipe as mp
import numpy as np
import time
import winsound
from collections import deque

# ================= CONFIG =================
TOTAL_TIME = 35
RATIO_STANDING = 0.75
RATIO_LUNGE = 0.40
CONFIRM_FRAMES = 4
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

lunge_count = 0
stage = "up"
data_sent = False

ratio_buffer = deque(maxlen=5)
up_frames = 0
down_frames = 0
last_rep_time = time.time()

# ================= HELPERS =================
def beep(freq=900, dur=120):
    try:
        winsound.Beep(freq, dur)
    except:
        pass

def get_grade(count):
    if count >= 20:
        return "GOOD"
    elif count >= 10:
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
            beep(1200, 400)

    skeleton_color = (255, 255, 255)

    # ================= LUNGE DETECTION =================
    if results.pose_landmarks and timer_running:
        lm = results.pose_landmarks.landmark

        # Choose more visible leg
        left_score = lm[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
        right_score = lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility

        if left_score > right_score:
            hip = lm[mp_pose.PoseLandmark.LEFT_HIP.value]
            knee = lm[mp_pose.PoseLandmark.LEFT_KNEE.value]
            shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        else:
            hip = lm[mp_pose.PoseLandmark.RIGHT_HIP.value]
            knee = lm[mp_pose.PoseLandmark.RIGHT_KNEE.value]
            shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

        if hip.visibility > 0.6 and knee.visibility > 0.6:
            torso_height = abs(shoulder.y - hip.y)
            thigh_vertical = abs(hip.y - knee.y)

            if torso_height > 0.05:
                raw_ratio = thigh_vertical / torso_height
                ratio_buffer.append(raw_ratio)
                smooth_ratio = sum(ratio_buffer) / len(ratio_buffer)

                cv2.putText(frame, f"Ratio: {smooth_ratio:.2f}",
                            (20, 150),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (255, 255, 255), 2)

                # ---- Stable Stage Logic ----
                if smooth_ratio > RATIO_STANDING:
                    up_frames += 1
                    down_frames = 0

                    if up_frames > CONFIRM_FRAMES:
                        stage = "up"
                        skeleton_color = (0, 0, 255)  # Red = standing

                elif smooth_ratio < RATIO_LUNGE:
                    down_frames += 1
                    up_frames = 0

                    if down_frames > CONFIRM_FRAMES and stage == "up":
                        stage = "down"
                        lunge_count += 1
                        last_rep_time = current_time
                        skeleton_color = (0, 255, 0)  # Green = good lunge
                        beep()
                else:
                    up_frames = 0
                    down_frames = 0

        # Idle detection
        if current_time - last_rep_time > IDLE_LIMIT:
            cv2.putText(frame, "KEEP MOVING!",
                        (20, 190),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 165, 255), 2)

    # ================= RESULT =================
    if not timer_running and remaining == 0 and start_time != 0:
        grade = get_grade(lunge_count)

        if not data_sent:
            send_workout_to_backend(
                "lunges",
                lunge_count,
                TOTAL_TIME,
                grade
            )
            data_sent = True

        cv2.putText(frame, "WORKOUT OVER",
                    (100, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (255, 255, 255), 3)

        cv2.putText(frame, f"Lunges: {lunge_count}",
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

        cv2.putText(frame, f"Lunges: {lunge_count}",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0, 255, 0), 2)

    # ================= SKELETON =================
    if results.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=skeleton_color, thickness=3, circle_radius=4),
            mp_draw.DrawingSpec(color=skeleton_color, thickness=2, circle_radius=2)
        )

    cv2.imshow("AI Lunge Trainer", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('s'):
        lunge_count = 0
        remaining = TOTAL_TIME
        start_time = time.time()
        timer_running = True
        data_sent = False
        up_frames = 0
        down_frames = 0
        last_rep_time = time.time()
        beep()

cap.release()
cv2.destroyAllWindows()