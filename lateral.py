import cv2
import mediapipe as mp
import numpy as np
import time
import winsound

# ===================== 1. SETUP & CONFIGURATION =====================
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

# ===================== CONSTANTS =====================
TOTAL_TIME = 60 
# Angle relative to torso (Shoulder-Hip-Elbow)
ANGLE_DOWN = 20    # Arms at sides
ANGLE_UP = 75      # Arms raised (approx shoulder height)

# ===================== FUNCTIONS =====================
def calculate_angle(a, b, c):
    """Calculates angle at B (Shoulder) between A (Hip) and C (Elbow)"""
    a = np.array(a) # Hip
    b = np.array(b) # Shoulder
    c = np.array(c) # Elbow
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    return angle

def beep(freq=800, dur=100):
    try: winsound.Beep(freq, dur)
    except: pass

# ===================== STATE VARIABLES =====================
timer_running = False
start_time = 0
remaining = TOTAL_TIME
raise_count = 0
stage = "down"
feedback = "Press 'S' to Start"
feedback_color = (0, 255, 255)

# ===================== MAIN LOOP =====================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    
    if timer_running:
        elapsed = int(time.time() - start_time)
        remaining = max(0, TOTAL_TIME - elapsed)
        if remaining <= 0: timer_running = False

    current_angle = 0
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        
        # We track the arm with better visibility
        l_vis = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility
        r_vis = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility
        
        if l_vis > r_vis:
            hip = [lm[mp_pose.PoseLandmark.LEFT_HIP.value].x, lm[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        else:
            hip = [lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x, lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

        current_angle = calculate_angle(hip, shoulder, elbow)

        # --- RAISE LOGIC ---
        if timer_running:
            # 1. Reached the top (Shoulder height)
            if current_angle > ANGLE_UP and stage == "down":
                stage = "up"
                raise_count += 1
                feedback = "GOOD RAISE!"
                feedback_color = (0, 255, 0)
                beep(1100, 100)
            
            # 2. Returned to bottom
            if current_angle < ANGLE_DOWN:
                stage = "down"
                feedback = "RAISE ARMS"
                feedback_color = (255, 255, 255)

            # 3. Warning: Going too high (risks impingement)
            if current_angle > 105:
                feedback = "TOO HIGH! STOP AT SHOULDERS"
                feedback_color = (0, 0, 255)

    # ===================== DRAWING UI =====================
    cv2.rectangle(frame, (0, 0), (450, 180), (0, 0, 0), -1)
    cv2.putText(frame, f"Time: {remaining}s", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"RAISES: {raise_count}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(frame, feedback, (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, feedback_color, 2)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        # Visual cue for angle
        cv2.putText(frame, f"{int(current_angle)} deg", 
                    tuple(np.multiply(shoulder, [w, h]).astype(int)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow("AI Lateral Raise Trainer", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    if key == ord('s'):
        raise_count, start_time, timer_running = 0, time.time(), True

cap.release()
cv2.destroyAllWindows()