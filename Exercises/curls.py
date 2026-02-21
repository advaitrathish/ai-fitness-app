from backend_sender import send_workout_to_backend
import cv2
import mediapipe as mp
import numpy as np
import time
import winsound
from collections import deque

# ================= CONFIG =================
TOTAL_TIME = 35
ANGLE_EXTENDED = 155
ANGLE_CURLED = 55
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

curl_count = 0
stage = "down"
data_sent = False

active_arm = None
angle_buffer = deque(maxlen=5)

up_frames = 0
down_frames = 0

# ================= HELPERS =================
def beep(freq=800, dur=120):
    try:
        winsound.Beep(freq, dur)
    except:
        pass

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

def get_grade(count):
    if count >= 18:
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
            beep(1200, 500)

    # ================= CURL DETECTION =================
    if results.pose_landmarks and timer_running:
        lm = results.pose_landmarks.landmark

        # Lock arm only once at start
        if active_arm is None:
            left_score = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility
            right_score = lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility
            active_arm = "left" if left_score > right_score else "right"

        if active_arm == "left":
            shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        else:
            shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                     lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                     lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        raw_angle = calculate_angle(shoulder, elbow, wrist)
        angle_buffer.append(raw_angle)
        smooth_angle = sum(angle_buffer) / len(angle_buffer)

        cv2.putText(frame, f"Angle: {int(smooth_angle)}",
                    (20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)

        # ---- Stable Detection Logic ----
        if smooth_angle > ANGLE_EXTENDED:
            down_frames += 1
            up_frames = 0

            if down_frames > CONFIRM_FRAMES:
                stage = "down"

        elif smooth_angle < ANGLE_CURLED:
            up_frames += 1
            down_frames = 0

            if up_frames > CONFIRM_FRAMES and stage == "down":
                stage = "up"
                curl_count += 1
                beep()

        else:
            up_frames = 0
            down_frames = 0

        # Draw Arm
        cv2.line(frame,
                 tuple(np.multiply(shoulder, [w, h]).astype(int)),
                 tuple(np.multiply(elbow, [w, h]).astype(int)),
                 (255, 255, 255), 3)

        cv2.line(frame,
                 tuple(np.multiply(elbow, [w, h]).astype(int)),
                 tuple(np.multiply(wrist, [w, h]).astype(int)),
                 (255, 255, 255), 3)

    # ================= RESULT =================
    if not timer_running and remaining == 0 and start_time != 0:
        grade = get_grade(curl_count)

        if not data_sent:
            send_workout_to_backend(
                "bicep_curls",
                curl_count,
                TOTAL_TIME,
                grade
            )
            data_sent = True

        cv2.putText(frame, "WORKOUT OVER",
                    (100, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (255, 255, 255), 3)

        cv2.putText(frame, f"Reps: {curl_count}",
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

        cv2.putText(frame, f"Reps: {curl_count}",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0, 255, 0), 2)

    cv2.imshow("AI Bicep Curl Trainer", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('s'):
        curl_count = 0
        remaining = TOTAL_TIME
        start_time = time.time()
        timer_running = True
        active_arm = None
        data_sent = False
        up_frames = 0
        down_frames = 0
        beep()

cap.release()
cv2.destroyAllWindows()