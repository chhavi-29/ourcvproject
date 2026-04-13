import cv2
import time
from sensors import WebcamSensor
from hand_tracker import HandTracker

class InputManager:
    def __init__(self):
        self.sensor = WebcamSensor()
        if not self.sensor.start():
            print("Warning: InputManager could not start the webcam.")
        self.tracker = HandTracker()
        self.last_time = time.time()
        self.last_pos = None

    def get_input(self):
        frame = self.sensor.read_frame()
        result = {
            "x": 0,
            "y": 0,
            "velocity": 0.0,
            "active": False,
            "frame": None
        }

        if frame is None:
            return result

        # Mirror mode
        frame = cv2.flip(frame, 1)
        result["frame"] = frame

        h, w = frame.shape[:2]
        self.tracker.process_frame(frame)
        self.tracker.draw_landmarks(frame) # DRAW SKELETON
        tip = self.tracker.get_index_tip(w, h)

        current_time = time.time()
        dt = current_time - self.last_time
        if dt <= 0:
            dt = 0.001
        self.last_time = current_time

        if tip:
            cam_x, cam_y = tip
            # Map from webcam resolution to 800x600 screen
            mapped_x = int((cam_x / w) * 800)
            mapped_y = int((cam_y / h) * 600)
            
            velocity = 0.0
            if self.last_pos:
                last_x, last_y = self.last_pos
                dist = ((mapped_x - last_x) ** 2 + (mapped_y - last_y) ** 2) ** 0.5
                velocity = dist / dt
            
            self.last_pos = (mapped_x, mapped_y)
            
            result["x"] = mapped_x
            result["y"] = mapped_y
            result["velocity"] = velocity
            result["active"] = True
        else:
            self.last_pos = None

        return result

    def stop(self):
        self.sensor.stop()

if __name__ == "__main__":
    manager = InputManager()
    print("Input Manager started. Press Q to exit.")
    while True:
        data = manager.get_input()
        frame = data["frame"]
        
        print(f"Active: {data['active']}, Pos: ({data['x']}, {data['y']}), Vel: {data['velocity']:.2f}")
        
        if frame is not None:
            cv2.imshow("Input Manager Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    manager.stop()
    cv2.destroyAllWindows()
