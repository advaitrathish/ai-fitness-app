from backend_sender import send_workout_to_backend
import cv2
import mediapipe as mp
import numpy as np
import time
import winsound
from collections import deque

# ================= CONFIG =================
TOTAL_TIME = 35
ANGLE_UP = 160
ANGLE_DOWN = 90
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

dip_count = 0
stage = "up"
data_sent = False

angle_buffer = deque(maxlen=5)
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

    # ================= TIMER =================
    if timer_running:
        elapsed = int(current_time - start_time)
        remaining = max(0, TOTAL_TIME - elapsed)

        if remaining == 0:
            timer_running = False
            beep(1200, 400)

    skeleton_color = (255, 255, 255)
    current_angle = 0

    # ================= DIP DETECTION =================
    if results.pose_landmarks and timer_running:
        lm = results.pose_landmarks.landmark

        left_vis = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility
        right_vis = lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility

        if left_vis > right_vis:
            shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            elbow = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]
        else:
            shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            elbow = lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        if elbow.visibility > 0.6:
            raw_angle = calculate_angle(
                [shoulder.x, shoulder.y],
                [elbow.x, elbow.y],
                [wrist.x, wrist.y]
            )

            angle_buffer.append(raw_angle)
            current_angle = int(sum(angle_buffer) / len(angle_buffer))

            # ---- STABLE LOGIC ----
            if current_angle > ANGLE_UP:
                up_frames += 1
                down_frames = 0

                if up_frames > CONFIRM_FRAMES:
                    stage = "up"
                    skeleton_color = (0, 0, 255)  # red = reset

            elif current_angle < ANGLE_DOWN:
                down_frames += 1
                up_frames = 0

                if down_frames > CONFIRM_FRAMES and stage == "up":
                    stage = "down"
                    dip_count += 1
                    last_rep_time = current_time
                    skeleton_color = (0, 255, 0)  # green = counted
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
        grade = get_grade(dip_count)

        if not data_sent:
            send_workout_to_backend(
                "tricepdips",
                dip_count,
                TOTAL_TIME,
                grade
            )
            data_sent = True

        cv2.putText(frame, "WORKOUT OVER",
                    (100, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (255, 255, 255), 3)

        cv2.putText(frame, f"Dips: {dip_count}",
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

        cv2.putText(frame, f"Dips: {dip_count}",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0, 255, 0), 2)

        cv2.putText(frame, f"Angle: {current_angle}",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 1)

    # ================= SKELETON =================
    if results.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=skeleton_color, thickness=3, circle_radius=4),
            mp_draw.DrawingSpec(color=skeleton_color, thickness=2, circle_radius=2)
        )

    cv2.imshow("AI Tricep Dip Trainer", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('s'):
        dip_count = 0
        remaining = TOTAL_TIME
        start_time = time.time()
        timer_running = True
        data_sent = False
        angle_buffer.clear()
        up_frames = 0
        down_frames = 0
        last_rep_time = time.time()
        beep()

cap.release()
cv2.destroyAllWindows()