from backend_sender import send_workout_to_backend
import cv2
import mediapipe as mp
import numpy as np
import time
import winsound
from collections import deque

# ================= CONFIG =================
TOTAL_TIME = 35
ANGLE_DOWN = 25
ANGLE_UP = 75
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

raise_count = 0
stage = "down"
data_sent = False

angle_buffer = deque(maxlen=5)
up_frames = 0
down_frames = 0

# ================= HELPERS =================
def beep(freq=900, dur=120):
    try:
        winsound.Beep(freq, dur)
    except:
        pass

def calculate_angle(a, b, c):
    a = np.array(a)  # Hip
    b = np.array(b)  # Shoulder
    c = np.array(c)  # Elbow

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

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

    # ================= RAISE DETECTION =================
    if results.pose_landmarks and timer_running:
        lm = results.pose_landmarks.landmark

        # Choose better visible side
        left_score = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility
        right_score = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility

        if left_score > right_score:
            hip = [
                lm[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                lm[mp_pose.PoseLandmark.LEFT_HIP.value].y
            ]
            shoulder = [
                lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
            ]
            elbow = [
                lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y
            ]
        else:
            hip = [
                lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y
            ]
            shoulder = [
                lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
            ]
            elbow = [
                lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y
            ]

        raw_angle = calculate_angle(hip, shoulder, elbow)
        angle_buffer.append(raw_angle)
        smooth_angle = sum(angle_buffer) / len(angle_buffer)

        cv2.putText(frame, f"Angle: {int(smooth_angle)}",
                    (20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)

        # ----- Stable Logic -----
        if smooth_angle < ANGLE_DOWN:
            down_frames += 1
            up_frames = 0

            if down_frames > CONFIRM_FRAMES:
                stage = "down"
                skeleton_color = (0, 0, 255)  # Red (arms down)

        elif ANGLE_UP < smooth_angle < 105:
            up_frames += 1
            down_frames = 0

            if up_frames > CONFIRM_FRAMES and stage == "down":
                stage = "up"
                raise_count += 1
                skeleton_color = (0, 255, 0)  # Green (correct raise)
                beep()
        else:
            up_frames = 0
            down_frames = 0

        # Safety warning
        if smooth_angle > 105:
            skeleton_color = (0, 0, 255)
            cv2.putText(frame, "STOP AT SHOULDER HEIGHT!",
                        (20, 190),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 0, 255), 2)

    # ================= RESULT =================
    if not timer_running and remaining == 0 and start_time != 0:
        grade = get_grade(raise_count)

        if not data_sent:
            send_workout_to_backend(
                "lateral_raises",
                raise_count,
                TOTAL_TIME,
                grade
            )
            data_sent = True

        cv2.putText(frame, "WORKOUT OVER",
                    (100, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (255, 255, 255), 3)

        cv2.putText(frame, f"Raises: {raise_count}",
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

        cv2.putText(frame, f"Raises: {raise_count}",
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

    cv2.imshow("AI Lateral Raise Trainer", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('s'):
        raise_count = 0
        remaining = TOTAL_TIME
        start_time = time.time()
        timer_running = True
        data_sent = False
        up_frames = 0
        down_frames = 0
        beep()

cap.release()
cv2.destroyAllWindows()