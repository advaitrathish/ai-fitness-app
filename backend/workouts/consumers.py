import json
import base64
import cv2
import numpy as np
import mediapipe as mp
import traceback

from channels.generic.websocket import AsyncWebsocketConsumer
from .engines.squat_engine import SquatEngine


mp_pose = mp.solutions.pose


class SquatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("WebSocket Connected")

        await self.accept()

        self.engine = SquatEngine()
        self.engine.start()

        # Lower confidence for easier detection
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    async def disconnect(self, close_code):
        print("WebSocket Disconnected")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            image_data = data.get("frame")

            if not image_data:
                print("No frame received")
                return

            print("Frame received")

            # =========================
            # Decode base64 image
            # =========================
            imgstr = image_data.split(',')[1]
            image_bytes = base64.b64decode(imgstr)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                print("Frame decode failed")
                return

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # =========================
            # Run MediaPipe
            # =========================
            results = self.pose.process(rgb_image)

            if results.pose_landmarks:
                print("Landmarks detected")

                response = self.engine.process_landmarks(
                    results.pose_landmarks.landmark
                )

            else:
                print("No landmarks detected")

                response = {
                    "count": self.engine.squat_count,
                    "feedback": "BODY NOT VISIBLE",
                    "grade": self.engine.get_grade(self.engine.squat_count),
                    "timer_running": True,
                }

            await self.send(text_data=json.dumps(response))

        except Exception as e:
            print("Error in WebSocket receive:")
            traceback.print_exc()

            await self.send(text_data=json.dumps({
                "count": 0,
                "feedback": "ERROR",
                "grade": "BAD",
                "timer_running": False,
            }))