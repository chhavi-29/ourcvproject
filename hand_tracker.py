import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        self.history = []

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)

    def get_index_tip(self, frame_w, frame_h):
        if self.results and self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[0]
            # Landmark 8 is the index finger tip
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_tip.x * frame_w), int(index_tip.y * frame_h)
            
            # Simple moving average over 2 frames to reduce lag but keep basic smoothing
            self.history.append((x, y))
            if len(self.history) > 2:
                self.history.pop(0)
            
            avg_x = int(sum(pt[0] for pt in self.history) / len(self.history))
            avg_y = int(sum(pt[1] for pt in self.history) / len(self.history))
            return (avg_x, avg_y)
        else:
            self.history = []
            return None

    def get_palm_center(self, frame_w, frame_h):
        if self.results and self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[0]
            # Landmark 0 is the wrist
            wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
            return int(wrist.x * frame_w), int(wrist.y * frame_h)
        return None

    def draw_landmarks(self, frame):
        if self.results and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

if __name__ == "__main__":
    from sensors import WebcamSensor
    
    sensor = WebcamSensor()
    if sensor.start():
        tracker = HandTracker()
        print("Hand Tracker started. Press Q to exit.")
        while True:
            frame = sensor.read_frame()
            if frame is None:
                break
            
            tracker.process_frame(frame)
            tracker.draw_landmarks(frame)
            
            h, w = frame.shape[:2]
            tip = tracker.get_index_tip(w, h)
            if tip:
                # Draw cyan circle at index tip
                cv2.circle(frame, tip, 10, (255, 255, 0), cv2.FILLED)
                
            cv2.imshow("Hand Tracking Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        sensor.stop()
        cv2.destroyAllWindows()
