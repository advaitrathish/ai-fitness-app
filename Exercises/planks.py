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
# Plank Grading (Total time held correctly)
# Good: Held for 60s+ within the 2 min window
# Average: Held for 30s-60s
# Bad: Held for < 30s

# Form Thresholds (Angles in Degrees)
# 180 is perfectly straight. We allow a small margin.
ANGLE_MIN = 165
ANGLE_MAX = 195

# ===================== STATE VARIABLES =====================
timer_running = False
start_time = 0
elapsed = 0
remaining = TOTAL_TIME

total_hold_time = 0.0 # Float to count seconds
last_frame_time = 0
form_good = False

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

def get_grade(seconds_held):
    if seconds_held >= 60:
        return "GOOD", (0, 255, 0)      
    elif 30 <= seconds_held < 60:
        return "AVERAGE", (0, 255, 255) 
    else:
        return "BAD", (0, 0, 255)       

def calculate_angle(a, b, c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

# ===================== MAIN LOOP =====================
last_timestamp = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Calculate Delta Time (for accurate hold counting)
    current_time = time.time()
    dt = current_time - last_timestamp
    last_timestamp = current_time

    # 1. Prepare Frame
    frame = cv2.flip(frame, 1) 
    h, w, _ = frame.shape
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    
    # 2. Timer Logic (Global 2-min Limit)
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

    # 3. Plank Logic (Form Check)
    current_angle = 0.0
    
    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        
        # Auto-detect side logic
        left_hip_vis = lm[mp_pose.PoseLandmark.LEFT_HIP.value].visibility
        right_hip_vis = lm[mp_pose.PoseLandmark.RIGHT_HIP.value].visibility

        if left_hip_vis > right_hip_vis:
            shoulder_lm = mp_pose.PoseLandmark.LEFT_SHOULDER
            hip_lm = mp_pose.PoseLandmark.LEFT_HIP
            ankle_lm = mp_pose.PoseLandmark.LEFT_ANKLE
        else:
            shoulder_lm = mp_pose.PoseLandmark.RIGHT_SHOULDER
            hip_lm = mp_pose.PoseLandmark.RIGHT_HIP
            ankle_lm = mp_pose.PoseLandmark.RIGHT_ANKLE

        # Get Coordinates
        shoulder = [lm[shoulder_lm.value].x, lm[shoulder_lm.value].y]
        hip = [lm[hip_lm.value].x, lm[hip_lm.value].y]
        ankle = [lm[ankle_lm.value].x, lm[ankle_lm.value].y]
        
        # Visibility Check
        if lm[hip_lm.value].visibility > 0.5:
            
            # --- ANGLE CALCULATION ---
            current_angle = calculate_angle(shoulder, hip, ankle)
            
            # --- HORIZONTAL CHECK ---
            # Ensure body is horizontal (X dist > Y dist)
            is_horizontal = abs(shoulder[0] - ankle[0]) > abs(shoulder[1] - ankle[1])

            # --- COUNTING LOGIC ---
            if timer_running:
                if not is_horizontal:
                    form_good = False
                    if not alert_active:
                        feedback = "GET DOWN (PLANK)"
                        feedback_color = (0, 255, 255)
                
                # Check for Straight Line (165 - 195 degrees)
                elif ANGLE_MIN < current_angle < ANGLE_MAX:
                    form_good = True
                    total_hold_time += dt  # Add time delta
                    if not alert_active:
                        feedback = "PERFECT FORM"
                        feedback_color = (0, 255, 0)
                
                else:
                    form_good = False
                    if not alert_active:
                        # Angle diagnostics
                        if current_angle < ANGLE_MIN:
                            feedback = "RAISE HIPS"
                        else:
                            feedback = "LOWER HIPS"
                        feedback_color = (0, 0, 255)
                        
                        # Warning beep every 2 seconds if form is bad
                        if int(current_time) % 2 == 0:
                            beep(600, 50)
                            
        else:
            form_good = False
            if not alert_active:
                feedback = "BODY NOT VISIBLE"
                feedback_color = (0, 0, 255)

    # ===================== DRAWING UI =====================
    
    # 4. Result Screen
    if not timer_running and remaining == 0 and start_time != 0:
        grade_text, grade_color = get_grade(total_hold_time)
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (w-50, h-50), (0,0,0), -1)
        frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
        
        cv2.putText(frame, "WORKOUT OVER", (w//2 - 180, h//2 - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"HELD: {int(total_hold_time)}s", (w//2 - 120, h//2), 
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

        # Show Total Time Held (This is the "Score")
        hold_color = (0, 255, 0) if form_good else (255, 255, 255)
        cv2.putText(frame, f"HELD: {int(total_hold_time)}s", (20, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, hold_color, 3)

        font_scale = 1.0 if alert_active else 0.7
        cv2.putText(frame, feedback, (20, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, feedback_color, 2)
        
        # Show Angle for debugging
        cv2.putText(frame, f"Hip Angle: {int(current_angle)}", (20, 185), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        if results.pose_landmarks:
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("AI Plank Trainer", frame)

    # ===================== INPUTS =====================
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        total_hold_time = 0
        elapsed = 0
        remaining = TOTAL_TIME
        start_time = time.time()
        last_timestamp = time.time()
        timer_running = True
        triggered_alerts = set()
        alert_active = False
        beep(800, 300)

cap.release()
cv2.destroyAllWindows()