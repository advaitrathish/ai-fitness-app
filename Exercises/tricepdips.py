import cv2
import mediapipe as mp
import numpy as np
import time
import winsound
from collections import deque

# ===================== 1. SETUP =====================
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

# ===================== CONSTANTS =====================
TOTAL_TIME = 120
# Strict Thresholds to prevent small movement counting
ANGLE_UP = 160    # Arm must be fully straight to reset
ANGLE_DOWN = 90   # Arm must be at 90 deg or lower to count

# ===================== VARIABLES =====================
timer_running = False
start_time = 0
elapsed = 0
remaining = TOTAL_TIME

dip_count = 0
stage = "up"
feedback = "Press 'S' to Start"
feedback_color = (0, 255, 255)

# SMOOTHING BUFFER: Stores last 7 angles to kill noise
angle_buffer = deque(maxlen=7)

# ===================== FUNCTIONS =====================
def calculate_angle(a, b, c):
    """Calculates angle at point B (elbow)"""
    a = np.array(a) # Shoulder
    b = np.array(b) # Elbow
    c = np.array(c) # Wrist
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0: angle = 360 - angle
    return angle

def beep(freq=800, dur=100):
    try: winsound.Beep(freq, dur)
    except: pass

def get_grade(count):
    if count >= 20: return "TITAN", (0, 255, 0)
    elif 12 <= count < 20: return "WARRIOR", (0, 255, 255)
    else: return "ROOKIE", (0, 0, 255)

# ===================== MAIN LOOP =====================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # 1. Processing
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    
    # 2. Timer
    if timer_running:
        elapsed = int(time.time() - start_time)
        remaining = max(0, TOTAL_TIME - elapsed)
        if remaining <= 0:
            timer_running = False
            feedback = "TIME OVER"
            beep(1500, 1000)

    # 3. Dip Logic
    current_angle = 0
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        
        # Auto-Side Detection
        l_vis = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility
        r_vis = lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility

        if l_vis > r_vis:
            shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x, lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        else:
            shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        # Raw Angle Calculation
        raw_angle = calculate_angle(shoulder, elbow, wrist)

        # --- SMOOTHING (Key Fix) ---
        angle_buffer.append(raw_angle)
        # We use the AVERAGE of the last 7 frames. 
        # This makes the angle count stable even if the camera is shaky.
        smooth_angle = int(sum(angle_buffer) / len(angle_buffer))
        current_angle = smooth_angle

        if timer_running:
            # UP PHASE: Arm must be VERY straight (> 160) to reset
            if smooth_angle > ANGLE_UP:
                stage = "up"
                feedback = "GO DOWN"
                feedback_color = (255, 255, 255)
            
            # DOWN PHASE: Arm must be VERY bent (< 90) to count
            elif smooth_angle < ANGLE_DOWN and stage == "up":
                stage = "down"
                dip_count += 1
                feedback = "GOOD REP!"
                feedback_color = (0, 255, 0)
                beep(1000, 150)
            
            # FEEDBACK FOR HALF REPS
            elif stage == "up" and smooth_angle < 130 and smooth_angle > 90:
                feedback = "LOWER!"
                feedback_color = (0, 165, 255)

        # Draw Skeleton
        cv2.circle(frame, (int(elbow[0]*w), int(elbow[1]*h)), 10, (0,0,255), -1)
        if 'shoulder' in locals():
            p1 = (int(shoulder[0]*w), int(shoulder[1]*h))
            p2 = (int(elbow[0]*w), int(elbow[1]*h))
            p3 = (int(wrist[0]*w), int(wrist[1]*h))
            cv2.line(frame, p1, p2, (255,255,255), 3)
            cv2.line(frame, p2, p3, (255,255,255), 3)

    # ===================== DRAW UI =====================
    # 1. Background
    cv2.rectangle(frame, (0, 0), (400, 220), (0, 0, 0), -1)
    
    # 2. Stats
    if not timer_running and remaining == 0:
        grade, color = get_grade(dip_count)
        cv2.putText(frame, f"GRADE: {grade}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    else:
        cv2.putText(frame, f"Time: {remaining}s", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"DIPS: {dip_count}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 4)
        cv2.putText(frame, feedback, (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, feedback_color, 2)
    
    # 3. VISUAL PROGRESS BAR (The Anti-Cheat visual)
    # Maps angle range [80, 170] to pixel range [20, 380]
    bar_width = 360
    bar_start_x = 20
    
    # Normalize angle to 0.0 - 1.0 range based on movement
    # 170 deg (straight) = 0% bar, 80 deg (bent) = 100% bar
    progress = np.interp(current_angle, [80, 170], [bar_width, 0])
    
    # Draw Empty Bar
    cv2.rectangle(frame, (bar_start_x, 180), (bar_start_x + bar_width, 200), (50, 50, 50), -1)
    
    # Draw Fill Bar
    cv2.rectangle(frame, (bar_start_x, 180), (bar_start_x + int(progress), 200), feedback_color, -1)
    
    # Draw Target Line (Green line at 90 deg mark)
    target_x = bar_start_x + int(np.interp(ANGLE_DOWN, [80, 170], [bar_width, 0]))
    cv2.line(frame, (target_x, 175), (target_x, 205), (0, 255, 0), 3)
    
    # Angle Text
    cv2.putText(frame, f"{current_angle} deg", (300, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.imshow("AI Dip Trainer Pro", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    if key == ord('s'):
        dip_count = 0
        start_time = time.time()
        timer_running = True
        angle_buffer.clear()
        beep(800, 300)

cap.release()
cv2.destroyAllWindows()