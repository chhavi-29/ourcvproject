import cv2

class WebcamSensor:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open webcam at index {self.camera_index}.")
            self.cap = None
            return False
        return True

    def read_frame(self):
        if self.cap is None:
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def stop(self):
        if self.cap:
            self.cap.release()
            self.cap = None

if __name__ == "__main__":
    sensor = WebcamSensor()
    if sensor.start():
        print("Webcam started. Press Q to exit.")
        while True:
            frame = sensor.read_frame()
            if frame is None:
                print("Failed to grab frame.")
                break
            cv2.imshow("Webcam Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        sensor.stop()
        cv2.destroyAllWindows()
