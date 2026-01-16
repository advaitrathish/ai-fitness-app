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
# Pushup Ratios (Arm Compression)
# 1.0 = Fully straight arm
# 0.6 = Deep pushup (90 degree bend)
RATIO_UP = 0.95   
RATIO_DOWN = 0.65 

# ===================== STATE VARIABLES =====================
timer_running = False
start_time = 0
elapsed = 0
remaining = TOTAL_TIME

pushup_count = 0
stage = "up"
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
    # Grading criteria for 2 mins (Adjustable)
    if count >= 20:
        return "GOOD", (0, 255, 0)      
    elif 12 <= count < 20:
        return "AVERAGE", (0, 255, 255) 
    else:
        return "BAD", (0, 0, 255)       

def calculate_distance(a, b):
    return np.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

# ===================== MAIN LOOP =====================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 1. Prepare Frame
    # For pushups, side view is best. 
    # Flip is optional depending on where you place the camera.
    frame = cv2.flip(frame, 1) 
    h, w, _ = frame.shape
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    
    # 2. Timer Logic
    current_time = time.time()
    
    if timer_running:
        elapsed = int(current_time - start_time)
        remaining = max(0, TOTAL_TIME - elapsed)
        
        # --- Time Alerts (30s, 10s, 5s) ---
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

    # 3. Pushup Logic (Arm Ratio)
    current_ratio = 0.0
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        
        # Check Visibility (Shoulder & Wrist)
        # We use LEFT side by default. If you show your RIGHT side, swap to RIGHT_xxx
        l_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        l_elbow = lm[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        l_wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]

        if l_shoulder.visibility > 0.5 and l_wrist.visibility > 0.5:
            
            # --- RATIO CALCULATION ---
            # Total length of the arm parts (Upper Arm + Forearm)
            full_arm_length = calculate_distance(l_shoulder, l_elbow) + calculate_distance(l_elbow, l_wrist)
            
            # Current straight-line distance from Shoulder to Wrist
            effective_length = calculate_distance(l_shoulder, l_wrist)

            # Ratio: If arm is straight, Ratio is ~1.0. If bent, Ratio drops.
            if full_arm_length > 0:
                current_ratio = effective_length / full_arm_length
            
            # --- COUNTING LOGIC ---
            if timer_running:
                # UP PHASE (Arm Straight)
                if current_ratio > RATIO_UP:
                    stage = "up"
                    if not alert_active: 
                        feedback = "GO DOWN"
                        feedback_color = (255, 255, 255)
                
                # DOWN PHASE (Arm Bent)
                elif current_ratio < RATIO_DOWN and stage == "up":
                    stage = "down"
                    pushup_count += 1
                    last_rep_time = time.time()
                    if not alert_active:
                        feedback = "GOOD PUSHUP!"
                        feedback_color = (0, 255, 0)
                    beep(1000, 150)

                # --- DISTRACTION CHECK (8s) ---
                if (time.time() - last_rep_time > 8) and not alert_active:
                    feedback = "KEEP MOVING!"
                    feedback_color = (0, 165, 255) # Orange
        else:
            if not alert_active:
                feedback = "SHOW FULL ARM"
                feedback_color = (0, 0, 255)

    # ===================== DRAWING UI =====================
    
    # 4. Result Screen
    if not timer_running and remaining == 0 and start_time != 0:
        grade_text, grade_color = get_grade(pushup_count)
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (0,0,0), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        
        cv2.putText(frame, "WORKOUT OVER", (w//2 - 180, h//2 - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"PUSHUPS: {pushup_count}", (w//2 - 120, h//2), 
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

        cv2.putText(frame, f"PUSHUPS: {pushup_count}", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        font_scale = 1.0 if alert_active else 0.7
        cv2.putText(frame, feedback, (20, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, feedback_color, 2)
        
        # Show Arm Ratio for debugging
        cv2.putText(frame, f"Arm Ratio: {current_ratio:.2f}", (20, 185), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        if results.pose_landmarks:
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("AI Pushup Trainer", frame)

    # ===================== INPUTS =====================
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        pushup_count = 0
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