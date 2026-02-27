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

  const stageRef = useRef<"up" | "down">("up");
  const angleBufferRef = useRef<number[]>([]);
  const lastRepTimeRef = useRef<number>(0);

  const upCounterRef = useRef(0);
  const downCounterRef = useRef(0);

  const calculateAngle = (a: any, b: any, c: any) => {
    const radians =
      Math.atan2(c.y - b.y, c.x - b.x) -
      Math.atan2(a.y - b.y, a.x - b.x);
    let angle = Math.abs((radians * 180) / Math.PI);
    if (angle > 180) angle = 360 - angle;
    return angle;
  };

  const smoothAngle = (raw: number) => {
    angleBufferRef.current.push(raw);
    if (angleBufferRef.current.length > 5)
      angleBufferRef.current.shift();
    return (
      angleBufferRef.current.reduce((a, b) => a + b, 0) /
      angleBufferRef.current.length
    );
  };

  const repAllowed = () => {
    const now = Date.now();
    if (now - lastRepTimeRef.current > 1000) {
      lastRepTimeRef.current = now;
      return true;
    }
    return false;
  };

  // Timer
  useEffect(() => {
    let interval: any;
    if (cameraOn) {
      interval = setInterval(() => {
        setSeconds((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [cameraOn]);

  useEffect(() => {
    if (!cameraOn) return;

    let camera: Camera;

    const pose = new Pose({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
    });

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      minDetectionConfidence: 0.6,
      minTrackingConfidence: 0.6,
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
        ctx.fillStyle = "rgba(0,0,0,0.6)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#ff4d4d";
        ctx.font = "22px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(
          "⚠ Full Body Not Visible",
          canvas.width / 2,
          canvas.height / 2
        );
        return;
      }

      const lm = results.poseLandmarks;

      drawConnectors(ctx, lm, POSE_CONNECTIONS, {
        color: "#00ffcc",
        lineWidth: 4,
      });

      drawLandmarks(ctx, lm, {
        color: "#ff00aa",
        lineWidth: 2,
      });

      const hip = lm[23];
      const knee = lm[25];
      const ankle = lm[27];
      const shoulder = lm[11];
      const elbow = lm[13];
      const wrist = lm[15];

      if (!hip || !knee || !ankle || !shoulder || !elbow || !wrist)
        return;

      if (
        hip.visibility < 0.6 ||
        knee.visibility < 0.6 ||
        ankle.visibility < 0.6
      )
        return;

      let rawAngle = 0;

      // =========================
      // SQUATS (unchanged)
      // =========================
      if (exerciseType === "squats") {
        rawAngle = calculateAngle(hip, knee, ankle);
        const angle = smoothAngle(rawAngle);

        const hipBelowKnee = hip.y > knee.y;

        if (
          angle < 90 &&
          hipBelowKnee &&
          stageRef.current === "up"
        ) {
          stageRef.current = "down";
          setFeedback("Go Up");
        }

        if (
          angle > 170 &&
          stageRef.current === "down"
        ) {
          if (repAllowed()) {
            stageRef.current = "up";
            setReps((prev) => prev + 1);
            setFeedback("Good Rep!");
          }
        }
      }

      // =========================
      // PUSHUPS (proper form check)
      // =========================
// =========================
// PUSHUPS (Optimized)
// =========================
if (exerciseType === "pushups") {
  // 1. Thresholds (Adjusted for side/angled view)
  const ANGLE_UP = 150;    // Arms straight-ish
  const ANGLE_DOWN = 90;   // Arms bent
  
  // 2. Identify landmarks (Using only what we need for pushups)
  const leftShoulder = lm[11];
  const leftElbow = lm[13];
  const leftWrist = lm[15];
  const rightShoulder = lm[12];
  const rightElbow = lm[14];
  const rightWrist = lm[16];

  // 3. Choose the arm that is more visible to the camera
  const leftVis = leftShoulder.visibility + leftElbow.visibility + leftWrist.visibility;
  const rightVis = rightShoulder.visibility + rightElbow.visibility + rightWrist.visibility;

  const s = leftVis > rightVis ? leftShoulder : rightShoulder;
  const e = leftVis > rightVis ? leftElbow : rightElbow;
  const w = leftVis > rightVis ? leftWrist : rightWrist;

  // 4. Check if we can actually see the arm
  if (s.visibility < 0.5 || e.visibility < 0.5) {
    setFeedback("Position your arm in view");
  } else {
    const rawAngle = calculateAngle(s, e, w);
    const angle = smoothAngle(rawAngle);

    // 5. State Machine Logic
    if (angle < ANGLE_DOWN) {
      if (stageRef.current === "up") {
        stageRef.current = "down";
        setFeedback("Push Up!");
      }
    } 
    
    if (angle > ANGLE_UP) {
      if (stageRef.current === "down") {
        if (repAllowed()) {
          stageRef.current = "up";
          setReps(prev => prev + 1);
          setFeedback("Great Rep!");
        }
      } else if (stageRef.current === "up") {
        setFeedback("Go Lower!");
      }
    }
  }
}
      // =========================
      // LUNGES
      // =========================
      if (exerciseType === "lunges") {
        rawAngle = calculateAngle(hip, knee, ankle);
        const angle = smoothAngle(rawAngle);

        if (
          angle < 85 &&
          stageRef.current === "up"
        ) {
          stageRef.current = "down";
        }

        if (
          angle > 170 &&
          stageRef.current === "down"
        ) {
          if (repAllowed()) {
            stageRef.current = "up";
            setReps((prev) => prev + 1);
            setFeedback("Nice Lunge!");
          }
        }
      }

      // =========================
      // BICEP CURLS
      // =========================
      if (exerciseType === "curls") {
        rawAngle = calculateAngle(shoulder, elbow, wrist);
        const angle = smoothAngle(rawAngle);

        if (angle < 60 && stageRef.current === "down") {
          stageRef.current = "up";
        }

        if (
          angle > 160 &&
          stageRef.current === "up"
        ) {
          if (repAllowed()) {
            stageRef.current = "down";
            setReps((prev) => prev + 1);
            setFeedback("Nice Curl!");
          }
        }
      }
    });

    if (videoRef.current) {
      camera = new Camera(videoRef.current, {
        onFrame: async () => {
          if (videoRef.current)
            await pose.send({ image: videoRef.current });
        },
        width: 640,
        height: 480,
      });
      camera.start();
    }

    return () => {
      if (camera) camera.stop();
    };
  }, [cameraOn, exerciseType]);

  return (
    <div className="p-10 text-white">
      <div className="flex justify-between mb-8">
        <h1 className="text-3xl font-bold">
          Live {exerciseType}
        </h1>
        <div className="text-gray-400">
          {new Date().toLocaleString()}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-8">

        <div className="col-span-2 bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={{ display: "none" }}
          />
          <canvas
            ref={canvasRef}
            className="rounded-xl w-full"
          />

          <button
            onClick={() => setCameraOn(!cameraOn)}
            className="mt-6 bg-gradient-to-r from-red-500 to-pink-500 px-6 py-3 rounded-xl"
          >
            {cameraOn ? "Stop" : "Start"}
          </button>
        </div>

        <div className="space-y-6">
          <StatCard title="Reps" value={reps} />
          <StatCard title="Timer" value={`${seconds}s`} />
          <StatCard title="Status" value={feedback} />
        </div>

      </div>
    </div>
  );
}

function StatCard({ title, value }: any) {
  return (
    <div className="bg-white/5 backdrop-blur-xl p-6 rounded-2xl border border-white/10">
      <p className="text-gray-400 text-sm">{title}</p>
      <h2 className="text-3xl font-bold mt-2">{value}</h2>
    </div>
  );
}