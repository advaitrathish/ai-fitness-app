import cv2
import mediapipe as mp
import numpy as np
import time
import winsound  # Windows only

# ===================== 1. SETUP & CONFIGURATION =====================
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

# ===================== CONSTANTS =====================
TOTAL_TIME = 120  # 2 Minutes
# Crunch Thresholds (Shoulder Y-Position relative to Hip)
# We calculate the angle of the torso relative to the ground.
# 0-10 degrees = Lying flat
# > 30 degrees = Crunched up
ANGLE_FLAT = 15   # Maximum angle to be considered "Down"
ANGLE_CRUNCH = 45 # Minimum angle to be considered "Up"

# ===================== STATE VARIABLES =====================
timer_running = False
start_time = 0
elapsed = 0
remaining = TOTAL_TIME

crunch_count = 0
stage = "down"
last_rep_time = 0

triggered_alerts = set()
feedback = "Press 'S' to Start"
feedback_color = (0, 255, 255) # Yellow
alert_active = False 

# ===================== FUNCTIONS =====================
def beep(freq=800, dur=100):
    try:
        winsound.Beep(freq, dur)
    except:
        pass

def get_grade(count):
    # Crunches are faster than pushups
    if count >= 30:
        return "GOOD", (0, 255, 0)      
    elif 15 <= count < 30:
        return "AVERAGE", (0, 255, 255) 
    else:
        return "BAD", (0, 0, 255)       

def calculate_angle_horizontal(a, b):
    """Calculates angle of line AB relative to horizontal axis"""
    a = np.array(a) # Shoulder
    b = np.array(b) # Hip
    
    # Calculate angle relative to horizontal (ground)
    radians = np.arctan2(abs(a[1]-b[1]), abs(a[0]-b[0]))
    angle = np.abs(radians * 180.0 / np.pi)
    return angle

# ===================== MAIN LOOP =====================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 1. Prepare Frame
    frame = cv2.flip(frame, 1) 
    h, w, _ = frame.shape
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    
    # 2. Timer Logic
    current_time = time.time()
    
    if timer_running:
        elapsed = int(current_time - start_time)
        remaining = max(0, TOTAL_TIME - elapsed)
        
        # --- Time Alerts ---
        if remaining in [30, 10, 5] and remaining not in triggered_alerts:
            triggered_alerts.add(remaining)
            alert_active = True
            feedback = f"{remaining} SECONDS LEFT!"
            feedback_color = (0, 0, 255) # Red
            beep(1000, 400) 
        elif remaining not in [30, 10, 5]:
            alert_active = False 

        # --- Time Over Check ---
        if remaining <= 0:
            timer_running = False
            feedback = "TIME OVER"
            beep(1500, 1000) 

    # 3. Crunch Logic
    current_angle = 0.0
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        
        # Detect Side (Left or Right)
        if lm[mp_pose.PoseLandmark.LEFT_HIP.value].visibility > lm[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility:
            shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hip = [lm[mp_pose.PoseLandmark.LEFT_HIP.value].x, lm[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        else:
            shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            hip = [lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x, lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

        # Calculate Torso Angle relative to ground
        current_angle = calculate_angle_horizontal(shoulder, hip)
            
        # --- COUNTING LOGIC ---
        if timer_running:
            # DOWN PHASE (Lying Flat)
            if current_angle < ANGLE_FLAT:
                stage = "down"
                if not alert_active: 
                    feedback = "CRUNCH UP"
                    feedback_color = (255, 255, 255)
            
            # UP PHASE (Sitting Up)
            elif current_angle > ANGLE_CRUNCH and stage == "down":
                stage = "up"
                crunch_count += 1
                last_rep_time = time.time()
                if not alert_active:
                    feedback = "GOOD CRUNCH!"
                    feedback_color = (0, 255, 0)
                beep(1000, 150)

            # --- DISTRACTION CHECK (8s) ---
            if (time.time() - last_rep_time > 8) and not alert_active:
                feedback = "KEEP GOING!"
                feedback_color = (0, 165, 255) # Orange

    # ===================== DRAWING UI =====================
    
    # 4. Result Screen
    if not timer_running and remaining == 0 and start_time != 0:
        grade_text, grade_color = get_grade(crunch_count)
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (0,0,0), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        
        cv2.putText(frame, "WORKOUT OVER", (w//2 - 180, h//2 - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"CRUNCHES: {crunch_count}", (w//2 - 120, h//2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"GRADE: {grade_text}", (w//2 - 160, h//2 + 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, grade_color, 4)
        cv2.putText(frame, "Press 'S' to Restart", (w//2 - 130, h-80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)

    # 5. Active UI
    else:
        cv2.rectangle(frame, (0, 0), (380, 200), (0, 0, 0), -1)

        cv2.putText(frame, f"Elapsed: {elapsed}s", (20, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        time_color = (0, 0, 255) if remaining <= 10 else (0, 255, 255)
        cv2.putText(frame, f"Left: {remaining}s", (200, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, time_color, 2)

        cv2.putText(frame, f"CRUNCHES: {crunch_count}", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        font_scale = 1.0 if alert_active else 0.7
        cv2.putText(frame, feedback, (20, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, feedback_color, 2)
        
        # Show Angle for debugging
        cv2.putText(frame, f"Torso Angle: {int(current_angle)}", (20, 185), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        if results.pose_landmarks:
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("AI Crunch Trainer", frame)

    # ===================== INPUTS =====================
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        crunch_count = 0
        elapsed = 0
        remaining = TOTAL_TIME
        start_time = time.time()
        last_rep_time = time.time()
        timer_running = True
        triggered_alerts = set()
        alert_active = False
        beep(800, 300)

cap.release()
cv2.destroyAllWindows()