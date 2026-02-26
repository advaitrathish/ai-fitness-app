import time


class SquatEngine:
    TOTAL_TIME = 40
    RATIO_STANDING = 1.6
    RATIO_SQUAT = 1.0

    def __init__(self):
        self.squat_count = 0
        self.stage = "up"
        self.start_time = None
        self.last_rep_time = None
        self.triggered_alerts = set()
        self.timer_running = False
        self.feedback = "Press Start"
        self.grade = "BAD"

    def start(self):
        self.squat_count = 0
        self.stage = "up"
        self.start_time = time.time()
        self.last_rep_time = time.time()
        self.triggered_alerts = set()
        self.timer_running = True
        self.feedback = "Workout Started"

    def stop(self):
        self.timer_running = False
        self.grade = self.get_grade(self.squat_count)

    def get_grade(self, count):
        if count >= 18:
            return "GOOD"
        elif 12 <= count < 18:
            return "AVERAGE"
        return "BAD"

    def process_landmarks(self, landmarks):
        """
        landmarks = mediapipe pose landmarks list
        """

        if not self.timer_running:
            return self._build_response()

        current_time = time.time()
        elapsed = int(current_time - self.start_time)
        remaining = max(0, self.TOTAL_TIME - elapsed)

        # TIMER ALERTS
        if remaining in [30, 10, 5] and remaining not in self.triggered_alerts:
            self.triggered_alerts.add(remaining)
            self.feedback = f"{remaining} SECONDS LEFT!"

        if remaining <= 0:
            self.stop()
            self.feedback = "TIME OVER"
            return self._build_response()

        # LANDMARK CHECK
        try:
            left_shoulder = landmarks[11]
            left_hip = landmarks[23]
            left_ankle = landmarks[27]

            torso_height = abs(left_hip.y - left_shoulder.y)
            leg_height = abs(left_ankle.y - left_hip.y)

            if torso_height > 0.05:
                ratio = leg_height / torso_height
            else:
                ratio = 0

            # Squat detection
            if ratio > self.RATIO_STANDING:
                self.stage = "up"
                self.feedback = "GO DOWN"

            elif ratio < self.RATIO_SQUAT and self.stage == "up":
                self.stage = "down"
                self.squat_count += 1
                self.last_rep_time = time.time()
                self.feedback = "GOOD REP"

            # Idle detection
            if (time.time() - self.last_rep_time) > 8:
                self.feedback = "IDLE / DISTRACTED"

        except Exception:
            self.feedback = "BODY NOT VISIBLE"

        return self._build_response()

    def _build_response(self):
        return {
            "count": self.squat_count,
            "feedback": self.feedback,
            "grade": self.get_grade(self.squat_count),
            "timer_running": self.timer_running,
        }