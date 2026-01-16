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
TOTAL_TIME = 40  # 2 Minutes Limit
RATIO_STANDING = 1.6  
RATIO_SQUAT = 1.0     

# ===================== STATE VARIABLES =====================
timer_running = False
start_time = 0
elapsed = 0
remaining = TOTAL_TIME

squat_count = 0
stage = "up"
last_rep_time = 0

# For Alerts
triggered_alerts = set()  # To make sure we only beep once per alert
feedback = "Press 'S' to Start"
feedback_color = (0, 255, 255) # Yellow
alert_active = False # To flash screen

# ===================== FUNCTIONS =====================
def beep(freq=800, dur=100):
    try:
        winsound.Beep(freq, dur)
    except:
        pass

def get_grade(count):
    if count >= 18:
        return "GOOD", (0, 255, 0)      # Green
    elif 12 <= count < 18:
        return "AVERAGE", (0, 255, 255) # Yellow
    else:
        return "BAD", (0, 0, 255)       # Red

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
            beep(1000, 400) # Longer beep
        elif remaining not in [30, 10, 5]:
            alert_active = False # Turn off flash

        # --- Time Over Check ---
        if remaining <= 0:
            timer_running = False
            feedback = "TIME OVER"
            beep(1500, 1000) # Long end beep

    # 3. Squat Logic (Proportion Based - UNCHANGED)
    current_ratio = 0.0
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        
        # Visibility Check
        left_hip_vis = lm[mp_pose.PoseLandmark.LEFT_HIP.value].visibility
        left_ankle_vis = lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility

        if left_hip_vis > 0.5 and left_ankle_vis > 0.5:
            # Coordinates
            shoulder_y = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
            hip_y = lm[mp_pose.PoseLandmark.LEFT_HIP.value].y
            ankle_y = lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].y

            torso_height = abs(hip_y - shoulder_y)
            leg_vertical_height = abs(ankle_y - hip_y)

            if torso_height > 0.05: 
                current_ratio = leg_vertical_height / torso_height
            
            # Counting
            if timer_running:
                # RESET / STANDING
                if current_ratio > RATIO_STANDING:
                    stage = "up"
                    if not alert_active: # Don't overwrite time alerts
                        feedback = "GO DOWN"
                        feedback_color = (255, 255, 255)
                
                # SQUAT DETECTED
                elif current_ratio < RATIO_SQUAT and stage == "up":
                    stage = "down"
                    squat_count += 1
                    last_rep_time = time.time()
                    if not alert_active:
                        feedback = "GOOD REP!"
                        feedback_color = (0, 255, 0)
                    beep(1000, 150)

                # --- DISTRACTION CHECK ---
                # If no rep for 8 seconds and time is running
                if (time.time() - last_rep_time > 8) and not alert_active:
                    feedback = "DISTRACTED / IDLE"
                    feedback_color = (0, 165, 255) # Orange
        else:
            if not alert_active:
                feedback = "FULL BODY NOT VISIBLE"
                feedback_color = (0, 0, 255)

    # ===================== DRAWING UI =====================
    
    # 4. Result Screen (If time is over)
    if not timer_running and remaining == 0 and start_time != 0:
        grade_text, grade_color = get_grade(squat_count)
        
        # Draw large semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (0,0,0), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        
        cv2.putText(frame, "WORKOUT OVER", (w//2 - 180, h//2 - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"SQUATS: {squat_count}", (w//2 - 120, h//2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"GRADE: {grade_text}", (w//2 - 160, h//2 + 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, grade_color, 4)
        
        cv2.putText(frame, "Press 'S' to Restart", (w//2 - 130, h-80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)

    # 5. Active Workout UI
    else:
        # Background Box
        cv2.rectangle(frame, (0, 0), (380, 200), (0, 0, 0), -1)

        # Timers
        cv2.putText(frame, f"Elapsed: {elapsed}s", (20, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        time_color = (0, 0, 255) if remaining <= 10 else (0, 255, 255)
        cv2.putText(frame, f"Left: {remaining}s", (200, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, time_color, 2)

        # Squat Count
        cv2.putText(frame, f"SQUATS: {squat_count}", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        # Status / Alerts
        # If alert is active, make text bigger and flash
        font_scale = 1.0 if alert_active else 0.7
        cv2.putText(frame, feedback, (20, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, feedback_color, 2)
        
        # Debug Ratio (Small)
        cv2.putText(frame, f"Ratio: {current_ratio:.2f}", (20, 185), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        # Draw Skeleton
        if results.pose_landmarks:
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("AI Squat Trainer - Final", frame)

    # ===================== INPUTS =====================
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        # RESET ALL VARIABLES
        squat_count = 0
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