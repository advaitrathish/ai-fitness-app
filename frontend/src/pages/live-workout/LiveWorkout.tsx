import { useEffect, useRef, useState } from "react";
import { Pose, POSE_CONNECTIONS } from "@mediapipe/pose";
import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { Camera } from "@mediapipe/camera_utils";

export default function LiveWorkout() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const cameraRef = useRef<any>(null);

  const [reps, setReps] = useState(0);
  const [feedback, setFeedback] = useState("Idle");
  const [grade, setGrade] = useState("BAD");
  const [cameraOn, setCameraOn] = useState(false);

  // =============================
  // WebSocket
  // =============================
  useEffect(() => {
    socketRef.current = new WebSocket("ws://127.0.0.1:8000/ws/squats/");

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setReps(data.count);
      setFeedback(data.feedback);
      setGrade(data.grade);
    };

    return () => {
      socketRef.current?.close();
    };
  }, []);

  // =============================
  // Start Camera + Skeleton
  // =============================
  const startCamera = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const pose = new Pose({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
    });

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });

    pose.onResults((results) => {
      const canvas = canvasRef.current!;
      const ctx = canvas.getContext("2d")!;
      canvas.width = videoRef.current!.videoWidth;
      canvas.height = videoRef.current!.videoHeight;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

      if (results.poseLandmarks) {
        drawConnectors(ctx, results.poseLandmarks, POSE_CONNECTIONS, {
          color: "#00FFAA",
          lineWidth: 4,
        });
        drawLandmarks(ctx, results.poseLandmarks, {
          color: "#FF00FF",
          lineWidth: 2,
        });
      }

      // Send frame to backend
      const frameData = canvas.toDataURL("image/jpeg");
      socketRef.current?.send(JSON.stringify({ frame: frameData }));
    });

    cameraRef.current = new Camera(videoRef.current, {
      onFrame: async () => {
        await pose.send({ image: videoRef.current! });
      },
      width: 640,
      height: 480,
    });

    cameraRef.current.start();
    setCameraOn(true);
  };

  // =============================
  // Stop Camera
  // =============================
  const stopCamera = () => {
    if (cameraRef.current) {
      cameraRef.current.stop();
      cameraRef.current = null;
    }

    const stream = videoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach((track) => track.stop());

    setCameraOn(false);
  };

  // =============================
  // Cleanup on page leave
  // =============================
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="p-8 grid lg:grid-cols-2 gap-8">
      {/* Left - Camera */}
      <div className="space-y-4">
        <video ref={videoRef} className="hidden" />
        <canvas ref={canvasRef} className="rounded-xl shadow-lg" />

        <div className="flex gap-4">
          {!cameraOn ? (
            <button
              onClick={startCamera}
              className="bg-green-500 text-white px-4 py-2 rounded-xl"
            >
              Start Camera
            </button>
          ) : (
            <button
              onClick={stopCamera}
              className="bg-red-500 text-white px-4 py-2 rounded-xl"
            >
              Stop Camera
            </button>
          )}
        </div>
      </div>

      {/* Right - Stats */}
      <div className="glass-card-strong p-6 space-y-6">
        <h2 className="text-2xl font-bold">Squats Workout</h2>

        <div className="text-xl">Reps: {reps}</div>
        <div className="text-xl">Feedback: {feedback}</div>
        <div className="text-xl">Grade: {grade}</div>
      </div>
    </div>
  );
}