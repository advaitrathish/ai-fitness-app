import { useEffect, useRef } from "react";
import { Pose, POSE_CONNECTIONS } from "@mediapipe/pose";
import { Camera } from "@mediapipe/camera_utils";
import * as drawingUtils from "@mediapipe/drawing_utils";

interface PoseCameraProps {
  onRep: () => void;
  isRunning: boolean;
}

export default function PoseCamera({ onRep, isRunning }: PoseCameraProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  let stage = "up";

  useEffect(() => {
    if (!videoRef.current || !canvasRef.current) return;

    const pose = new Pose({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
    });

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      minDetectionConfidence: 0.6,
      minTrackingConfidence: 0.6,
    });

    pose.onResults((results) => {
      const canvasCtx = canvasRef.current!.getContext("2d")!;
      canvasCtx.save();
      canvasCtx.clearRect(
        0,
        0,
        canvasRef.current!.width,
        canvasRef.current!.height
      );

      canvasCtx.drawImage(
        results.image,
        0,
        0,
        canvasRef.current!.width,
        canvasRef.current!.height
      );

      if (results.poseLandmarks) {
        drawingUtils.drawConnectors(
        canvasCtx,
        results.poseLandmarks,
        POSE_CONNECTIONS
        );

        drawingUtils.drawLandmarks(canvasCtx, results.poseLandmarks);

        // =========================
        // Squat Detection Logic
        // =========================

        const leftHip = results.poseLandmarks[23];
        const leftAnkle = results.poseLandmarks[27];
        const leftShoulder = results.poseLandmarks[11];

        const torsoHeight = Math.abs(leftHip.y - leftShoulder.y);
        const legHeight = Math.abs(leftAnkle.y - leftHip.y);

        const ratio = legHeight / torsoHeight;

        if (ratio > 1.6) {
          stage = "up";
        }

        if (ratio < 1.0 && stage === "up" && isRunning) {
          stage = "down";
          onRep();
        }
      }

      canvasCtx.restore();
    });

    const camera = new Camera(videoRef.current, {
      onFrame: async () => {
        await pose.send({ image: videoRef.current! });
      },
      width: 640,
      height: 480,
    });

    camera.start();

    return () => {
      camera.stop();
    };
  }, [isRunning]);

  return (
    <div className="relative">
      <video ref={videoRef} className="hidden" />
      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        className="rounded-xl"
      />
    </div>
  );
}