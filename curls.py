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
TOTAL_TIME = 60
# Adjusted Thresholds for realistic movement
ANGLE_EXTENDED = 160  # Arm needs to be straight (Reset point)
ANGLE_CURLED = 50     # Arm fully bent (Count point) - Relaxed from 35 to 50

# ===================== VARIABLES =====================
timer_running = False
start_time = 0
elapsed = 0
remaining = TOTAL_TIME

curl_count = 0
stage = "down"
feedback = "Press 'S' to Start"
feedback_color = (0, 255, 255)

# Smoothing Buffer (Stores last 5 angles to remove jitter)
angle_buffer = deque(maxlen=5)

# Arm Locking (Prevents switching left/right mid-set)
active_arm = None  # Will be 'left' or 'right'

# ===================== FUNCTIONS =====================
def calculate_angle(a, b, c):
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

# ===================== MAIN LOOP =====================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # 1. Image Processing
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    
    # 2. Timer Management
    if timer_running:
        elapsed = int(time.time() - start_time)
        remaining = max(0, TOTAL_TIME - elapsed)
        if remaining <= 0:
            timer_running = False
            feedback = "TIME OVER"
            beep(1500, 1000)

    # 3. Angle Calculation
    current_angle = 0
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        
        # --- ARM LOCKING LOGIC ---
        # Only decide which arm to track when the timer starts
        if active_arm is None:
            l_vis = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility
            r_vis = lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility
            active_arm = "left" if l_vis > r_vis else "right"
        
        # Select Landmarks based on locked arm
        if active_arm == "left":
            shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x, lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        else:
            shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        # Calculate Raw Angle
        raw_angle = calculate_angle(shoulder, elbow, wrist)
        
        # --- SMOOTHING LOGIC ---
        angle_buffer.append(raw_angle)
        smooth_angle = sum(angle_buffer) / len(angle_buffer)
        current_angle = int(smooth_angle)

        # --- CURL REP LOGIC ---
        if timer_running:
            # DOWN PHASE (Extension)
            if smooth_angle > ANGLE_EXTENDED:
                stage = "down"
                feedback = "CURL UP"
                feedback_color = (255, 255, 255)

            # UP PHASE (Flexion)
            # Only triggers if previous stage was 'down' (Full ROM required)
            elif smooth_angle < ANGLE_CURLED and stage == "down":
                stage = "up"
                curl_count += 1
                feedback = "GOOD REP!"
                feedback_color = (0, 255, 0)
                beep(1000, 150)

        # Visualization: Draw Arm Skeleton
        cv2.line(frame, tuple(np.multiply(shoulder, [w, h]).astype(int)), 
                 tuple(np.multiply(elbow, [w, h]).astype(int)), (255, 255, 255), 3)
        cv2.line(frame, tuple(np.multiply(elbow, [w, h]).astype(int)), 
                 tuple(np.multiply(wrist, [w, h]).astype(int)), (255, 255, 255), 3)
        cv2.circle(frame, tuple(np.multiply(elbow, [w, h]).astype(int)), 10, (0, 0, 255), -1)

    # ===================== UI DRAWING =====================
    # Background
    cv2.rectangle(frame, (0, 0), (400, 200), (0, 0, 0), -1)
    
    # Stats
    cv2.putText(frame, f"Time: {remaining}s", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f"REPS: {curl_count}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 4)
    cv2.putText(frame, f"Stage: {stage}", (250, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    # Angle Meter
    cv2.putText(frame, f"Angle: {current_angle}", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    
    # Threshold Bars (Visual Guide)
    # Map angle 180->30 to x-coordinate 20->300
    bar_x = int(np.interp(current_angle, [30, 180], [300, 20]))
    cv2.rectangle(frame, (20, 170), (300, 190), (100, 100, 100), -1) # Track
    cv2.rectangle(frame, (bar_x, 165), (bar_x+10, 195), feedback_color, -1) # Slider
    
    # Target Zones on Bar
    cv2.line(frame, (int(np.interp(ANGLE_CURLED, [30, 180], [300, 20])), 170), 
             (int(np.interp(ANGLE_CURLED, [30, 180], [300, 20])), 190), (0, 255, 0), 3) # Green Zone
    
    cv2.putText(frame, feedback, (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, feedback_color, 2)

    cv2.imshow("AI Bicep Trainer", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    if key == ord('s'):
        # Reset everything
        curl_count = 0
        start_time = time.time()
        timer_running = True
        active_arm = None # Re-calibrate arm
        beep(800, 300)

cap.release()
cv2.destroyAllWindows()