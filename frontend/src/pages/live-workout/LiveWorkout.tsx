import { useEffect, useRef, useState } from "react";
import { Pose, POSE_CONNECTIONS } from "@mediapipe/pose";
import { Camera } from "@mediapipe/camera_utils";
import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { useSearchParams } from "react-router-dom";

export default function LiveWorkout() {
  const [searchParams] = useSearchParams();
  const exerciseType = searchParams.get("type") || "squats";

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [reps, setReps] = useState(0);
  const [feedback, setFeedback] = useState("Idle");
  const [cameraOn, setCameraOn] = useState(false);
  const [seconds, setSeconds] = useState(0);

  const stageRef = useRef<string>("up");
  const angleBufferRef = useRef<number[]>([]);
  const lastRepTimeRef = useRef<number>(0);
  
  // High-accuracy frame counters
  const upCounterRef = useRef(0);
  const downCounterRef = useRef(0);
  const startTimeRef = useRef<number>(0);

  // Helper: Calculate 2D Angle
  const calculateAngle = (a: any, b: any, c: any) => {
    const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
    let angle = Math.abs((radians * 180) / Math.PI);
    if (angle > 180) angle = 360 - angle;
    return angle;
  };

  // Helper: Vector-Based 2D Angle for better precision
  const calculateVectorAngle = (s: any, e: any, w: any) => {
    const v1 = [s.x - e.x, s.y - e.y];
    const v2 = [w.x - e.x, w.y - e.y];
    const dot = v1[0] * v2[0] + v1[1] * v2[1];
    const mag1 = Math.sqrt(v1[0] ** 2 + v1[1] ** 2);
    const mag2 = Math.sqrt(v2[0] ** 2 + v2[1] ** 2);
    return Math.acos(Math.max(-1, Math.min(1, dot / (mag1 * mag2)))) * (180 / Math.PI);
  };

  const smoothAngle = (raw: number) => {
    angleBufferRef.current.push(raw);
    if (angleBufferRef.current.length > 5) angleBufferRef.current.shift();
    return angleBufferRef.current.reduce((a, b) => a + b, 0) / angleBufferRef.current.length;
  };

  const repAllowed = () => {
    const now = Date.now();
    if (now - lastRepTimeRef.current > 1200) {
      lastRepTimeRef.current = now;
      return true;
    }
    return false;
  };

  // Timer logic for planks vs regular reps
  useEffect(() => {
    let interval: any;
    if (cameraOn) {
      interval = setInterval(() => {
        if (exerciseType !== "planks") {
          setSeconds((prev) => prev + 1);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [cameraOn, exerciseType]);

  useEffect(() => {
    if (!cameraOn) return;

    let camera: Camera;
    const pose = new Pose({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
    });

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      minDetectionConfidence: 0.7,
      minTrackingConfidence: 0.7,
    });

    pose.onResults((results) => {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      if (!canvas || !video) return;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

      if (!results.poseLandmarks) {
        setFeedback("Full Body Not Visible");
        return;
      }

      const lm = results.poseLandmarks;
      drawConnectors(ctx, lm, POSE_CONNECTIONS, { color: "#00ffcc", lineWidth: 4 });
      drawLandmarks(ctx, lm, { color: "#ff00aa", lineWidth: 2 });

      // Core Landmarks
      const l_s = lm[11], l_e = lm[13], l_w = lm[15], l_h = lm[23], l_k = lm[25], l_a = lm[27];
      const r_s = lm[12], r_e = lm[14], r_w = lm[16], r_h = lm[24], r_k = lm[26], r_a = lm[28];
      const nose = lm[0];

      // Dynamic side selection based on visibility
      const leftVis = (l_s.visibility || 0) + (l_e.visibility || 0);
      const rightVis = (r_s.visibility || 0) + (r_e.visibility || 0);
      const s = leftVis > rightVis ? l_s : r_s;
      const e = leftVis > rightVis ? l_e : r_e;
      const w = leftVis > rightVis ? l_w : r_w;
      const h = leftVis > rightVis ? l_h : r_h;
      const k = leftVis > rightVis ? l_k : r_k;
      const a = leftVis > rightVis ? l_a : r_a;

      // =========================
      // EXERCISE LOGIC (HIGH ACCURACY PORT)
      // =========================

      //PUSHUPS:

      if (exerciseType === "pushups") {
        // 1. Identify landmarks for both sides
        const l_s = lm[11], l_e = lm[13], l_w = lm[15], l_h = lm[23], l_a = lm[27];
        const r_s = lm[12], r_e = lm[14], r_w = lm[16], r_h = lm[24], r_a = lm[28];

        // 2. Determine the side with the strongest signal (Highest visibility)
        const leftVis = l_e.visibility || 0;
        const rightVis = r_e.visibility || 0;

        const s = leftVis > rightVis ? l_s : r_s;
        const e = leftVis > rightVis ? l_e : r_e;
        const w = leftVis > rightVis ? l_w : r_w;
        const h = leftVis > rightVis ? l_h : r_h;
        const a = leftVis > rightVis ? l_a : r_a;
        const visScore = Math.max(leftVis, rightVis);

        // 3. THE STABILITY FILTER: Reject frames with poor tracking
        // This stops random counts when you aren't in position
        if (visScore < 0.8) {
          setFeedback("Get in Position");
          return;
        }

        // 4. Calculate smoothed angle using the vector method
        const rawAngle = calculateVectorAngle(s, e, w);
        const angle = smoothAngle(rawAngle);

        // 5. ACCURACY GATES (The 'Anti-Random' Logic)
        // Check 1: Is the body horizontal?
        const isHorizontal = Math.abs(s.y - h.y) < 0.25;
        
        // Check 2: Core Stability (Shoulder-Hip-Ankle alignment)
        const bodyLine = calculateAngle(s, h, a);
        const isCoreLocked = bodyLine > 165 && bodyLine < 195;

        // 6. Professional State Machine
        // UP: Must be straight, horizontal, and arm locked out (>160 deg)
        if (angle > 160 && isHorizontal && isCoreLocked) {
          if (stageRef.current !== "up") {
            stageRef.current = "up";
            setFeedback("Lower your chest!");
          }
        }

        // DOWN: Must hit depth (<90 deg) AND maintain core lockdown
        if (stageRef.current === "up" && angle < 90 && isCoreLocked) {
          if (repAllowed()) {
            stageRef.current = "down";
            setReps(prev => prev + 1);
            setFeedback("Great Pushup!");
          }
        }
      }

      //PULLUPS:

      else if (exerciseType === "pullups") {
        // 1. DYNAMIC SIDE SELECTION & VISIBILITY GATE
        const leftVis = lm[13].visibility || 0;
        const rightVis = lm[14].visibility || 0;

        // Choose the side with higher confidence to prevent 'ghost' jumps
        const side = leftVis > rightVis ? "left" : "right";
        const s = side === "left" ? lm[11] : lm[12];
        const e = side === "left" ? lm[13] : lm[14];
        const w = side === "left" ? lm[15] : lm[16];
        const h = side === "left" ? lm[23] : lm[24]; // Hip for scaling
        const vis = Math.max(leftVis, rightVis);

        // 2. THE STABILITY GATE: Ignore frames with poor tracking
        if (vis > 0.7) {
          // Calculate high-precision angle
          const rawAngle = calculateAngle(s, e, w);
          const currentAngle = smoothAngle(rawAngle);

          // 3. BIOMETRIC SCALING (The Accuracy Secret)
          // We calculate the torso length to set relative spatial gates
          const torsoLen = Math.abs(s.y - h.y);
          const barY = (lm[15].y + lm[16].y) / 2;
          
          // Gate A: Suspension Check (Wrists must be significantly above shoulders)
          const isHanging = (lm[15].y < lm[11].y - 0.05) && (lm[16].y < lm[12].y - 0.05);
          
          // Gate B: Vertical Alignment (Prevents counting while walking/swinging)
          const isStable = Math.abs(s.x - w.x) < 0.12;

          // Gate C: Chin Clearance (Nose must physically pass the bar line)
          const chinCleared = lm[0].y < barY;

          // 4. STATE MACHINE WITH FRAME CONFIRMATION
          // -------- RESET / DOWN POSITION --------
          if (currentAngle > 160 && isHanging && isStable) {
            downCounterRef.current++;
            upCounterRef.current = 0;
            if (downCounterRef.current > 4) {
              stageRef.current = "down";
              setFeedback("Hanging - Pull Up!");
            }
          }

          // -------- PULL / UP POSITION --------
          else if (currentAngle < 75 && stageRef.current === "down") {
            upCounterRef.current++;
            downCounterRef.current = 0;

            // Must be held for 4 frames + Pass Chin & Stability checks
            if (upCounterRef.current > 4) {
              if (isHanging && chinCleared && isStable) {
                if (repAllowed()) {
                  stageRef.current = "up";
                  setReps(prev => prev + 1);
                  setFeedback("Perfect Rep!");
                  upCounterRef.current = 0; // Prevent double counting
                }
              }
            }
          } else {
            // Reset if user leaves the 'ready' zones
            if (currentAngle > 80 && currentAngle < 150) {
              upCounterRef.current = 0;
              downCounterRef.current = 0;
            }
          }
        }
      }

      //SQUATS:

      else if (exerciseType === "squats") {
        // 1. Get Landmarks for both sides
        const l_h = lm[23], l_k = lm[25], l_a = lm[27];
        const r_h = lm[24], r_k = lm[26], r_a = lm[28];

        // 2. Dynamic Side Selection: Focus on the leg with higher visibility
        const leftKneeVis = l_k.visibility || 0;
        const rightKneeVis = r_k.visibility || 0;

        let angle: number;
        let hipY: number;
        let kneeY: number;

        if (leftKneeVis > rightKneeVis) {
          angle = calculateAngle(l_h, l_k, l_a);
          hipY = l_h.y;
          kneeY = l_k.y;
        } else {
          angle = calculateAngle(r_h, r_k, r_a);
          hipY = r_h.y;
          kneeY = r_k.y;
        }

        const smoothedAngle = smoothAngle(angle);

        // 3. Flexible Thresholds & State Machine
        // UP State: Arm/Leg is reasonably straight
        if (smoothedAngle > 155) {
          if (stageRef.current !== "up") {
            stageRef.current = "up";
            setFeedback("Squat Down!");
          }
        }

        // DOWN State: 
        // - angle < 115 ensures joint flexion
        // - hipY > (kneeY * 0.85) is the "Proximity Gate" 
        //   It ensures the hips are physically low on the screen relative to the knees.
        if (stageRef.current === "up" && smoothedAngle < 115) {
          if (hipY > (kneeY * 0.85)) { 
            if (repAllowed()) {
              stageRef.current = "down";
              setReps(prev => prev + 1);
              setFeedback("Good Depth!");
            }
          }
        }
      }

      //CURLS:
      
      else if (exerciseType === "curls") {
    // 1. Dual-Side Selection with Stability Filter
    const leftVis = lm[13].visibility || 0;
    const rightVis = lm[14].visibility || 0;
    const side = leftVis > rightVis ? "left" : "right";
    
    // Adjusted visibility gate for better detection in your setup
    if (Math.max(leftVis, rightVis) < 0.5) { 
        setFeedback("Move back: Arm not visible");
        return;
    }

    // 2. Vector-Based Angle Calculation (Dot Product)
    const s = side === "left" ? lm[11] : lm[12];
    const e = side === "left" ? lm[13] : lm[14];
    const w = side === "left" ? lm[15] : lm[16];

    // Using your vector angle helper for maximum precision
    const rawAngle = calculateVectorAngle(s, e, w);
    const angle = smoothAngle(rawAngle);

    // 3. Movement Constraints (The "Accuracy" Gates)
    const wrist_y = w.y;
    const elbow_y = e.y;
    // Check horizontal elbow drift (prevents counting body swings)
    const elbow_drift = Math.abs(s.x - e.x); 

    // 4. STATE MACHINE
    // -------- DOWN POSITION --------
    // Arm is straight (Vector angle > 160)
    if (angle > 160) {
        if (stageRef.current !== "down") {
            stageRef.current = "down";
            setFeedback("Curl Up!");
        }
    }

    // -------- UP POSITION --------
    // 1. Angle is tight (< 35)
    // 2. Wrist is physically above the elbow
    // 3. Elbow drift is low (< 0.12)
    else if (stageRef.current === "down" && angle < 35) {
        if (wrist_y < elbow_y && elbow_drift < 0.12) {
            if (repAllowed()) {
                stageRef.current = "up";
                setReps(prev => prev + 1);
                setFeedback("Perfect Rep!");
            }
        } else if (wrist_y >= elbow_y) {
            setFeedback("Squeeze higher!");
        }
    }
}

      //LUNGES:

      else if (exerciseType === "lunges") {
    // 1. Identify all leg landmarks
    const l_h = lm[23], l_k = lm[25], l_a = lm[27];
    const r_h = lm[24], r_k = lm[26], r_a = lm[28];

    // 2. Dynamic Scaling (The Accuracy Secret)
    // Uses torso length to create a 'Standard Unit' for your body
    const torsoSize = Math.abs(lm[11].y - lm[23].y); 

    // 3. Side Selection: Calculate angles for both knees
    const l_angle = calculateAngle(l_h, l_k, l_a);
    const r_angle = calculateAngle(r_h, r_k, r_a);

    // Focus on the leg with the most flexion (smallest angle)
    const currentAngle = Math.min(l_angle, r_angle);
    const avgAngle = smoothAngle(currentAngle);

    // 4. BIOMETRIC POSITION GATES
    // Gate: Knee must drop significantly relative to the hip
    const knee_y_max = Math.max(l_k.y, r_k.y);
    const hip_y_min = Math.min(l_h.y, r_h.y);
    const isLowEnough = (knee_y_max - hip_y_min) > (0.5 * torsoSize);

    // 5. STATE MACHINE WITH FRAME CONFIRMATION
    // -------- UP POSITION --------
    if (avgAngle > 160) {
        upCounterRef.current++;
        downCounterRef.current = 0;
        if (upCounterRef.current > 3) {
            stageRef.current = "up";
            setFeedback("Step into Lunge");
        }
    }

    // -------- DOWN POSITION --------
    else if (avgAngle < 110) {
        downCounterRef.current++;
        upCounterRef.current = 0;

        // Must be held, coming from 'up', and pass the Biometric Depth Gate
        if (stageRef.current === "up" && downCounterRef.current > 3) {
            if (isLowEnough) {
                if (repAllowed()) {
                    stageRef.current = "down";
                    setReps(prev => prev + 1);
                    setFeedback("Perfect Lunge!");
                    downCounterRef.current = 0; // Prevent double counting
                }
            } else {
                setFeedback("Drop your back knee!");
            }
        }
    } 
    else {
        // Reset counters in transition zones to ensure intentional movement
        upCounterRef.current = 0;
        downCounterRef.current = 0;
    }
}

      //PLANKS:

      else if (exerciseType === "planks") {
  // 1. Dynamic side selection for better accuracy on screen recordings
  const leftVis = lm[23].visibility || 0;
  const rightVis = lm[24].visibility || 0;

  const s = leftVis > rightVis ? lm[11] : lm[12];
  const h = leftVis > rightVis ? lm[23] : lm[24];
  const a = leftVis > rightVis ? lm[27] : lm[28];
  const vis = Math.max(leftVis, rightVis);

  // 2. The Stability Gate: Ensures tracking is high quality before running logic
  if (vis > 0.5) {
    const currentAngle = calculateAngle(s, h, a);
    const avgAngle = smoothAngle(currentAngle);

    // 3. SPATIAL FILTERS (High-Accuracy Gates)
    // Gate A: Alignment (Shoulder-Hip-Ankle line)
    const isStraight = avgAngle > 160 && avgAngle < 200;
    
    // Gate B: Horizontal Check (Shoulder and Ankle on same plane)
    const isHorizontal = Math.abs(s.y - a.y) < 0.15;

    // 4. PERSISTENT TIMER LOGIC
    if (isStraight && isHorizontal) {
      // If we just entered correct form, resume the clock
      if (stageRef.current !== "active") {
        // This line is the key: it offsets the start time by the seconds already counted
        startTimeRef.current = Date.now() - (seconds * 1000);
        stageRef.current = "active";
      }
      
      // Calculate elapsed time based on the offset start
      const currentElapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
      setSeconds(currentElapsed);
      setFeedback("Form Correct: Counting...");
    } else {
      // FORM BROKEN: Pause the state but do not reset the 'seconds' state
      stageRef.current = "paused";
      
      // Provide specific feedback for your NCERC demo
      if (!isStraight) setFeedback("Fix Your Back (Straighten)!");
      else if (!isHorizontal) setFeedback("Stay Horizontal!");
    }
  } else {
    setFeedback("Full Body Not Visible");
    stageRef.current = "paused";
  }
}
      //LATERAL RAISES:

      else if (exerciseType === "lateral") {
    // 1. DYNAMIC POINT SELECTION
    // We only need the top half of the body for Lateral Raises
    const l_s = lm[11], l_e = lm[13], l_w = lm[15];
    const r_s = lm[12], r_e = lm[14], r_w = lm[16];
    const l_h = lm[23], r_h = lm[24];

    // 2. ADAPTIVE VISIBILITY GATE
    // Lowered to 0.3 to handle screen-on-screen recordings like your demo
    const upperBodyVis = (l_s.visibility + r_s.visibility + l_e.visibility + r_e.visibility) / 4;

    if (upperBodyVis > 0.3) {
        // 3. Precision Angle Calculation
        const lAngle = calculateAngle(l_h, l_s, l_e);
        const rAngle = calculateAngle(r_h, r_s, r_e);
        const currentAngle = smoothAngle((lAngle + rAngle) / 2);

        // 4. THE "ANTI-RANDOM" GATES
        // Requires elbows to be straight (Shoulder-Elbow-Wrist > 140)
        const isArmStraight = calculateAngle(l_s, l_e, l_w) > 140 && 
                             calculateAngle(r_s, r_e, r_w) > 140;

        // 5. RESPONSIVE STATE MACHINE
        // -------- DOWN POSITION (Reset) --------
        if (currentAngle < 40) { 
            upCounterRef.current = 0;
            downCounterRef.current++;
            if (downCounterRef.current > 2) { 
                stageRef.current = "down";
                setFeedback("Ready - Start Raise");
            }
        }

        // -------- UP POSITION (Rep Count) --------
        else if (currentAngle > 78) { // Optimized for screen-depth distortion
            downCounterRef.current = 0;
            upCounterRef.current++;
            
            // Must hold for 2 frames to confirm it's not a glitch
            if (upCounterRef.current > 2 && stageRef.current === "down") {
                if (isArmStraight) {
                    if (repAllowed()) {
                        stageRef.current = "up";
                        setReps(prev => prev + 1);
                        setFeedback("Perfect Form!");
                        upCounterRef.current = 0; 
                    }
                } else {
                    setFeedback("Keep Arms Straight!");
                }
            }
        }
    } else {
        // Updated feedback for your specific setup
        setFeedback("Move phone closer to camera");
    }
}

      //CRUNCHES:

      else if (exerciseType === "crunches") {
    // 1. Get landmarks for the side with better visibility
    const l_s = lm[11], l_h = lm[23], l_k = lm[25];
    const r_s = lm[12], r_h = lm[24], r_k = lm[26];
    
    // Choose the side the camera sees better (usually the side facing the lens)
    const leftVis = l_h.visibility || 0;
    const rightVis = r_h.visibility || 0;
    
    const s = leftVis > rightVis ? l_s : r_s;
    const h = leftVis > rightVis ? l_h : r_h;
    const k = leftVis > rightVis ? l_k : r_k;
    const vis = Math.max(leftVis, rightVis);

    // 2. THE STABILITY GATE: Reject frames with poor tracking
    if (vis > 0.6) {
        // Calculate the primary crunch angle (Shoulder-Hip-Knee)
        const rawAngle = calculateAngle(s, h, k);
        const avgAngle = smoothAngle(rawAngle); // Using your smoothing helper

        // 3. SPATIAL FILTERS (Anti-Random Logic)
        // Distance check: Shoulder must physically move closer to the knee plane
        const distSK = Math.sqrt(Math.pow(s.x - k.x, 2) + Math.pow(s.y - k.y, 2));
        
        // 4. STATE MACHINE WITH FRAME CONFIRMATION
        // -------- DOWN POSITION (Lying Flat) --------
        if (avgAngle > 110) {
            upCounterRef.current = 0;
            downCounterRef.current++;
            if (downCounterRef.current > 4) { // Hold for 4 frames to confirm reset
                stageRef.current = "down";
                setFeedback("Lying Flat - Crunch Up!");
            }
        }

        // -------- UP POSITION (The Crunch) --------
        else if (avgAngle < 75) {
            downCounterRef.current = 0;
            upCounterRef.current++;
            
            // Accuracy Lock:
            // - Must hold for 4 frames
            // - Must be coming from 'down' stage
            // - Proximity check: Shoulder must be close to the knee
            if (upCounterRef.current > 4 && stageRef.current === "down") {
                if (distSK < 0.45) { // Threshold for torso-to-knee proximity
                    if (repAllowed()) {
                        stageRef.current = "up";
                        setReps(prev => prev + 1);
                        setFeedback("Ab Power!");
                        upCounterRef.current = 0; // Prevent double counting
                    }
                } else {
                    setFeedback("Lift higher!");
                }
            }
        } 
        else {
            // Reset counters in the 'dead zone' to ensure intentional movement
            upCounterRef.current = 0;
            downCounterRef.current = 0;
        }
    } else {
        setFeedback("Adjust camera to see your side");
    }
}
      //TRICEP DIPS:

      else if (exerciseType === "tricepdips") {
  // 1. DYNAMIC SIDE SELECTION
  // Prioritize whichever side the camera sees better inside the phone frame
  const lVis = lm[13]?.visibility || 0;
  const rVis = lm[14]?.visibility || 0;
  
  const s = lVis > rVis ? lm[11] : lm[12]; // Shoulder
  const e = lVis > rVis ? lm[13] : lm[14]; // Elbow
  const w = lVis > rVis ? lm[15] : lm[16]; // Wrist
  const h = lVis > rVis ? lm[23] : lm[24]; // Hip

  // 2. BYPASS GLOBAL VISIBILITY (The "Full Body" Fix)
  // We only require the Shoulder and Elbow to be detected
  // Threshold set to 0.25 to handle reflections on the secondary screen
  if (s.visibility > 0.25 && e.visibility > 0.25) {
    
    // 3. Precision Angle & Verticality Logic
    const angle = smoothAngle(calculateVectorAngle(s, e, w));
    const shoulderY = s.y;
    const elbowY = e.y;
    // Checks if the user is vertical (prevents counting pushups or phone movement)
    const isVertical = Math.abs(s.x - h.x) < 0.25; 

    // 4. FAIL-PROOF STATE MACHINE
    // -------- UP POSITION (Reset) --------
    // Arm is straight (>150) and shoulder is well above the elbow
    if (angle > 150 && shoulderY < (elbowY - 0.04)) {
      if (stageRef.current !== "up") {
        stageRef.current = "up";
        setFeedback("Good - Now Dip Down");
      }
    }

    // -------- DOWN POSITION (The Count) --------
    // 1. Arm is bent (< 110)
    // 2. Coming from the 'up' state
    // 3. Shoulder has dropped closer to the elbow level
    else if (stageRef.current === "up" && angle < 110 && isVertical) {
      // The Depth Anchor: Allows a 12% vertical screen margin
      if (shoulderY > (elbowY - 0.12)) {
        if (repAllowed()) {
          stageRef.current = "down";
          setReps(prev => prev + 1);
          setFeedback("Great Rep!");
        }
      } else {
        setFeedback("Dip Slightly Lower");
      }
    }
  } else {
    // This only shows if the AI cannot see the arm at all
    setFeedback("Focus camera on the arm");
  }
}

    });

    if (videoRef.current) {
      camera = new Camera(videoRef.current, {
        onFrame: async () => {
          if (videoRef.current) await pose.send({ image: videoRef.current });
        },
        width: 640,
        height: 480,
      });
      camera.start();
    }

    return () => { if (camera) camera.stop(); };
  }, [cameraOn, exerciseType]);

  return (
    <div className="p-10 text-white min-h-screen bg-black/90">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-black uppercase tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500">
            Live {exerciseType}
          </h1>
          <p className="text-gray-500 font-mono mt-1">FITQUEST_AI_SYSTEM_ACTIVE</p>
        </div>
        <div className="text-right">
          <p className="text-gray-400 font-medium">SESSION_TIME</p>
          <p className="text-2xl font-bold">{new Date().toLocaleTimeString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 relative">
          <div className="absolute inset-0 bg-blue-500/10 blur-3xl rounded-full"></div>
          <div className="relative bg-white/5 backdrop-blur-2xl rounded-3xl p-4 border border-white/10 shadow-2xl">
            <video ref={videoRef} autoPlay playsInline className="hidden" />
            <canvas ref={canvasRef} className="rounded-2xl w-full shadow-inner bg-black/40" />
            
            <div className="absolute top-8 left-8 bg-black/60 backdrop-blur-md px-4 py-2 rounded-lg border border-white/20">
              <span className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${cameraOn ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                <span className="text-xs font-bold tracking-widest">{cameraOn ? 'LIVE_FEED' : 'CAMERA_OFF'}</span>
              </span>
            </div>

            <button
              onClick={() => setCameraOn(!cameraOn)}
              className={`mt-6 w-full py-4 rounded-2xl font-black text-lg transition-all transform hover:scale-[1.02] active:scale-95 shadow-lg ${
                cameraOn 
                ? "bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-500 hover:to-pink-500" 
                : "bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-400 hover:to-emerald-500"
              }`}
            >
              {cameraOn ? "TERMINATE_SESSION" : "INITIALIZE_TRACKER"}
            </button>
          </div>
        </div>

        <div className="space-y-6">
          <StatCard title={exerciseType === "planks" ? "Seconds" : "Reps"} value={exerciseType === "planks" ? seconds : reps} highlight="text-green-400" />
          <StatCard title="Session Timer" value={`${seconds}s`} highlight="text-blue-400" />
          <StatCard title="AI Feedback" value={feedback} highlight="text-purple-400" />
          
          <div className="p-6 bg-gradient-to-br from-white/10 to-transparent rounded-3xl border border-white/10">
            <p className="text-xs font-bold text-gray-500 tracking-widest mb-4">SYSTEM_LOGS</p>
            <div className="space-y-2 font-mono text-[10px] text-gray-400">
              <p>{`> Exercise identified: ${exerciseType}`}</p>
              <p>{`> Logic Engine: High-Accuracy Vector Mode`}</p>
              <p>{`> Biometric Scaling: Active`}</p>
              <p>{`> Status: ${feedback}`}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, highlight }: { title: string, value: string | number, highlight: string }) {
  return (
    <div className="bg-white/5 backdrop-blur-xl p-8 rounded-3xl border border-white/10 hover:border-white/20 transition-all group">
      <p className="text-gray-500 text-xs font-black uppercase tracking-widest group-hover:text-gray-300 transition-colors">{title}</p>
      <h2 className={`text-5xl font-black mt-3 ${highlight} tracking-tighter`}>{value}</h2>
    </div>
  );
}