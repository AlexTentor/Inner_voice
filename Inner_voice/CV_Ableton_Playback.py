from ultralytics import YOLO
from pythonosc import udp_client
import cv2
import math 
import time


# OSC Setup
IP_local = "127.0.0.1"
OSC_port = 11000 #Ableton API port 
client = udp_client.SimpleUDPClient(IP_local, OSC_port)

# start webcam
cap = cv2.VideoCapture(0)
cap.set(3, 4000)
cap.set(4, 4000)

# model
model = YOLO("yolo-Weights/yolov8n.pt")

# object classes
#classNames = []
classNames = model.names

while True:
    success, img = cap.read()
    frame = [100,0, 100,0]
    results = model(img, stream=True, conf=0.03, classes=41)


    # coordinates
    for r in results:
        resultados = []
        boxes = r.boxes

        seconds = time.time()
    

        for box in boxes:
            # bounding box
            # confidence
            confidence = math.ceil((box.conf[0]*100))/100

            # class name
            cls = int(box.cls[0])
        
            print("Class name -->", classNames[cls])
            nombres = str("[" + classNames[cls] + "]")
            resultados.append(nombres
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # put box in cam
            cv2.rectangle(img, (x1, y1), (x2, y2), (cls*2, 0, cls), 3)

            # object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 5
            color = (cls, 0, 0)
            thickness = 2

            cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)
    object_to_detect = "[cup]"
    if (object_to_detec in resultados):
                client.send_message("/live/song/continue_playing" , None)
    if (object_to_detec not in resultados):
                client.send_message("/live/song/stop_playing" , None)
    # Optional resize image 
    # imS = cv2.resize(img, (480, 270))               

    cv2.imshow('Webcam', imS)
    if cv2.waitKey(1) == ord('q'):
        client.send_message("/live/song/stop_playing" , None)
        break

cap.release()
cv2.destroyAllWindows()
