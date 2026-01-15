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
# Lunge Ratios (Vertical Thigh Height / Torso Height)
# We measure how "vertical" the thigh is.
# RATIO > 0.8: Thigh is vertical (Standing)
# RATIO < 0.3: Thigh is horizontal (Hip and Knee are at same height)
RATIO_STANDING = 0.8  
RATIO_LUNGE = 0.35     

# ===================== STATE VARIABLES =====================
timer_running = False
start_time = 0
elapsed = 0
remaining = TOTAL_TIME

lunge_count = 0
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
    # Lunge grading (Total reps, usually alternating legs)
    if count >= 20:
        return "GOOD", (0, 255, 0)      
    elif 12 <= count < 20:
        return "AVERAGE", (0, 255, 255) 
    else:
        return "BAD", (0, 0, 255)       

# ===================== MAIN LOOP =====================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 1. Prepare Frame
    # Side view is best for lunges
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

    # 3. Lunge Logic
    current_ratio = 0.0
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        
        # Auto-detect side: Check which knee is more visible/forward
        # But generally, we just check the most visible leg.
        left_knee_vis = lm[mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
        right_knee_vis = lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility
        
        # Select landmarks based on visibility
        if left_knee_vis > right_knee_vis:
            hip = lm[mp_pose.PoseLandmark.LEFT_HIP.value]
            knee = lm[mp_pose.PoseLandmark.LEFT_KNEE.value]
            shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        else:
            hip = lm[mp_pose.PoseLandmark.RIGHT_HIP.value]
            knee = lm[mp_pose.PoseLandmark.RIGHT_KNEE.value]
            shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

        # Ensure visibility
        if hip.visibility > 0.5 and knee.visibility > 0.5:
            
            # --- RATIO CALCULATION ---
            # 1. Torso Length (Shoulder to Hip Vertical Dist)
            torso_height = abs(shoulder.y - hip.y)
            
            # 2. Thigh Vertical Height (Hip to Knee Vertical Dist)
            # When standing, this is large. When lunging (thigh parallel), this is small.
            thigh_vertical_height = abs(hip.y - knee.y)
            
            # Calculate Ratio
            if torso_height > 0.05:
                current_ratio = thigh_vertical_height / torso_height
            
            # --- COUNTING LOGIC ---
            if timer_running:
                # UP PHASE (Standing)
                # Thigh is vertical, so ratio is high
                if current_ratio > RATIO_STANDING:
                    stage = "up"
                    if not alert_active: 
                        feedback = "STEP/LUNGE"
                        feedback_color = (255, 255, 255)
                
                # DOWN PHASE (Lunge)
                # Thigh is horizontal, so vertical height drops (ratio drops)
                elif current_ratio < RATIO_LUNGE and stage == "up":
                    stage = "down"
                    lunge_count += 1
                    last_rep_time = time.time()
                    if not alert_active:
                        feedback = "GOOD LUNGE!"
                        feedback_color = (0, 255, 0)
                    beep(1000, 150)

                # --- DISTRACTION CHECK (8s) ---
                if (time.time() - last_rep_time > 8) and not alert_active:
                    feedback = "KEEP MOVING!"
                    feedback_color = (0, 165, 255) # Orange
        else:
            if not alert_active:
                feedback = "SHOW FULL BODY"
                feedback_color = (0, 0, 255)

    # ===================== DRAWING UI =====================
    
    # 4. Result Screen
    if not timer_running and remaining == 0 and start_time != 0:
        grade_text, grade_color = get_grade(lunge_count)
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (0,0,0), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        
        cv2.putText(frame, "WORKOUT OVER", (w//2 - 180, h//2 - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"LUNGES: {lunge_count}", (w//2 - 120, h//2), 
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

        cv2.putText(frame, f"LUNGES: {lunge_count}", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        font_scale = 1.0 if alert_active else 0.7
        cv2.putText(frame, feedback, (20, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, feedback_color, 2)
        
        # Show Thigh Ratio for debugging
        cv2.putText(frame, f"Thigh Ratio: {current_ratio:.2f}", (20, 185), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        if results.pose_landmarks:
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("AI Lunge Trainer", frame)

    # ===================== INPUTS =====================
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        lunge_count = 0
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