from picamera2 import Picamera2
import time

picam2 = Picamera2()
picam2.start()

time.sleep(2)

for i in range(5):
    filename = f"photo_{i:03d}.jpg"
    picam2.capture_file(filename)

    print(filename)

    time.sleep(0.5)

picam2.stop()