from backend_sender import send_workout_to_backend
import cv2
import mediapipe as mp
import numpy as np
import time
import winsound

# ================= CONFIG =================
TOTAL_TIME = 45
ANGLE_UP = 160
ANGLE_DOWN = 95
CONFIRM_FRAMES = 4
IDLE_LIMIT = 4

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.7,
                    min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

# ================= STATE =================
timer_running = False
start_time = 0
remaining = TOTAL_TIME

pushup_count = 0
stage = "up"
data_sent = False

up_counter = 0
down_counter = 0
last_rep_time = time.time()

# ================= HELPERS =================
def beep(freq=800, dur=150):
    try:
        winsound.Beep(freq, dur)
    except:
        pass

def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

def get_grade(count):
    if count >= 15:
        return "GOOD"
    elif count >= 8:
        return "AVERAGE"
    return "BAD"

# ================= MAIN LOOP =================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
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

    # ================= PUSHUP DETECTION =================
    if results.pose_landmarks and timer_running:
        lm = results.pose_landmarks.landmark

        # Choose better visible arm
        left_score = (
            lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility +
            lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility +
            lm[mp_pose.PoseLandmark.LEFT_WRIST.value].visibility
        )

        right_score = (
            lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility +
            lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility +
            lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].visibility
        )

        if left_score > right_score:
            shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            elbow = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value]
            wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]
        else:
            shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            elbow = lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        if shoulder.visibility > 0.6 and wrist.visibility > 0.6:
            angle = calculate_angle(shoulder, elbow, wrist)

            cv2.putText(frame, f"Angle: {int(angle)}",
                        (20, 150),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2)

            # UP detection (must stay above threshold for few frames)
            if angle > ANGLE_UP:
                up_counter += 1
                down_counter = 0
                if up_counter > CONFIRM_FRAMES:
                    stage = "up"

            # DOWN detection (must stay below threshold for few frames)
            elif angle < ANGLE_DOWN:
                down_counter += 1
                up_counter = 0

                if down_counter > CONFIRM_FRAMES and stage == "up":
                    stage = "down"
                    pushup_count += 1
                    last_rep_time = current_time
                    beep()
            else:
                up_counter = 0
                down_counter = 0

    # Idle detection
    if timer_running and current_time - last_rep_time > IDLE_LIMIT:
        cv2.putText(frame, "START MOVING!",
                    (20, 190),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 255), 2)

    # ================= RESULT =================
    if not timer_running and remaining == 0 and start_time != 0:
        grade = get_grade(pushup_count)

        if not data_sent:
            send_workout_to_backend(
                "pushups",
                pushup_count,
                TOTAL_TIME,
                grade
            )
            data_sent = True

        cv2.putText(frame, "WORKOUT OVER",
                    (100, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (255, 255, 255), 3)

        cv2.putText(frame, f"Pushups: {pushup_count}",
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

        cv2.putText(frame, f"Pushups: {pushup_count}",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0, 255, 0), 2)

        if results.pose_landmarks:
            mp_draw.draw_landmarks(frame,
                                   results.pose_landmarks,
                                   mp_pose.POSE_CONNECTIONS)

    cv2.imshow("AI Pushup Trainer - Stable", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

    if key == ord('s'):
        pushup_count = 0
        remaining = TOTAL_TIME
        start_time = time.time()
        timer_running = True
        data_sent = False
        last_rep_time = time.time()
        up_counter = 0
        down_counter = 0
        beep()

cap.release()
cv2.destroyAllWindows()