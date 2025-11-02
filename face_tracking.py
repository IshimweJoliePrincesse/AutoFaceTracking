import cv2
import time
import serial
# ----------- SERIAL CONFIGURATION -----------
# Make sure to replace COM3 with your Arduino port (e.g., COM5, /dev/ttyUSB0, etc.)
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=1)
time.sleep(2)  # wait for Arduino to initialize
print("[INFO] Connected to Arduino :white_check_mark:")
# --------------------------------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0)
prev_center = None
prev_time = time.time()
direction = "CENTER"
print("[INFO] Face Left-Right Tracker Started (press 'q' to quit)")
while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Camera not accessible.")
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    primary_face = None
    max_area = 0
    # Select largest detected face
    for (x, y, w, h) in faces:
        if w * h > max_area:
            max_area = w * h
            primary_face = (x, y, w, h)
    if primary_face:
        x, y, w, h = primary_face
        cx, cy = x + w // 2, y + h // 2
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 4, (255, 0, 0), -1)
        current_time = time.time()
        dt = current_time - prev_time if prev_time else 1e-6
        if prev_center:
            dx = cx - prev_center[0]
            if abs(dx) > 8:
                if dx > 0:
                    direction = "RIGHT"
                    arduino.write(b'rotate 90\n')
                    print("[CMD] Sent → rotate 90 (RIGHT)")
                else:
                    direction = "LEFT"
                    arduino.write(b'rotate -90\n')
                    print("[CMD] Sent → rotate -90 (LEFT)")
            else:
                direction = "CENTER"
        prev_center = (cx, cy)
        prev_time = current_time
        if direction in ["LEFT", "RIGHT"]:
            cv2.putText(frame, direction, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 3)
        else:
            cv2.putText(frame, "CENTER", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
    else:
        cv2.putText(frame, "NO FACE DETECTED", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.imshow("Face-Controlled Stepper Motor", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[INFO] Exiting...")
        break
cap.release()
arduino.close()
cv2.destroyAllWindows()