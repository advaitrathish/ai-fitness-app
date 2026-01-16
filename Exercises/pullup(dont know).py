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
# Pull-up Thresholds (Nose vs Wrist Y-position)
# MediaPipe Y-coordinates: 0 is Top of screen, 1 is Bottom.
# So, smaller Y means "Higher" on screen.

# To count as UP: Nose Y must be close to Wrist Y (or above it)
# Threshold: Positive value means Nose is below Wrist. Negative means Nose is above Wrist.
THRESHOLD_UP = 0.05   # Nose is very close to wrist height (or above)
THRESHOLD_DOWN = 0.25 # Nose is significantly below wrist (arms straight)

# ===================== STATE VARIABLES =====================
timer_running = False
start_time = 0
elapsed = 0
remaining = TOTAL_TIME

pullup_count = 0
stage = "down" # Start in the 'down' hanging position
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
    # Pull-ups are harder, so the grading scale is lower
    if count >= 15:
        return "GOOD", (0, 255, 0)      
    elif 8 <= count < 15:
        return "AVERAGE", (0, 255, 255) 
    else:
        return "BAD", (0, 0, 255)       

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

    # 3. Pull-Up Logic (Nose vs Wrist)
    current_dist = 0.0
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        
        # Check Visibility
        nose = lm[mp_pose.PoseLandmark.NOSE.value]
        left_wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]

        # Ensure we can see the upper body
        if nose.visibility > 0.5 and left_wrist.visibility > 0.5:
            
            # Use the average height of both wrists for accuracy
            avg_wrist_y = (left_wrist.y + right_wrist.y) / 2
            
            # Calculate vertical distance: Nose Y - Wrist Y
            # Positive = Nose is BELOW wrists (Hanging)
            # Negative = Nose is ABOVE wrists (Chin up)
            vertical_dist = nose.y - avg_wrist_y
            
            # --- COUNTING LOGIC ---
            if timer_running:
                # DOWN PHASE (Hanging)
                # If nose is far below wrist
                if vertical_dist > THRESHOLD_DOWN:
                    stage = "down"
                    if not alert_active: 
                        feedback = "PULL UP"
                        feedback_color = (255, 255, 255)
                
                # UP PHASE (Chin Up)
                # If nose passes the wrist line
                elif vertical_dist < THRESHOLD_UP and stage == "down":
                    stage = "up"
                    pullup_count += 1
                    last_rep_time = time.time()
                    if not alert_active:
                        feedback = "GOOD PULL-UP!"
                        feedback_color = (0, 255, 0)
                    beep(1000, 150)

                # --- DISTRACTION CHECK (8s) ---
                if (time.time() - last_rep_time > 8) and not alert_active:
                    feedback = "DON'T STOP!"
                    feedback_color = (0, 165, 255) # Orange
        else:
            if not alert_active:
                feedback = "SHOW HEAD & HANDS"
                feedback_color = (0, 0, 255)

    # ===================== DRAWING UI =====================
    
    # 4. Result Screen
    if not timer_running and remaining == 0 and start_time != 0:
        grade_text, grade_color = get_grade(pullup_count)
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (0,0,0), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        
        cv2.putText(frame, "WORKOUT OVER", (w//2 - 180, h//2 - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"PULL-UPS: {pullup_count}", (w//2 - 120, h//2), 
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

        cv2.putText(frame, f"PULL-UPS: {pullup_count}", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        font_scale = 1.0 if alert_active else 0.7
        cv2.putText(frame, feedback, (20, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, feedback_color, 2)
        
        # Show Vertical Dist for debugging
        if 'vertical_dist' in locals():
            cv2.putText(frame, f"Nose-Wrist Dist: {vertical_dist:.2f}", (20, 185), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        if results.pose_landmarks:
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("AI Pull-Up Trainer", frame)

    # ===================== INPUTS =====================
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        pullup_count = 0
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