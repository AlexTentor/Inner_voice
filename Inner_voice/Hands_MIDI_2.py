import cv2
import math
import mediapipe as mp
from pythonosc import udp_client
import mido
import numpy as np

# Setup
out_port = mido.open_output("to Max 1")
client = udp_client.SimpleUDPClient("127.0.0.1", 7400)

# MediaPipe setup with custom config
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=0  # Use simpler model for better performance
)
mp_draw = mp.solutions.drawing_utils

# Video capture with explicit dimensions
cap = cv2.VideoCapture(0)
width = 640
height = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Create projection matrix
camera_matrix = np.array([[width, 0, width/2],
                         [0, height, height/2],
                         [0, 0, 1]], dtype=float)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process with explicit image dimensions
    results = hands.process(image)
    
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract points 4 and 8
            p4 = (int(hand_landmarks.landmark[4].x * width), 
                  int(hand_landmarks.landmark[4].y * height))
            p8 = (int(hand_landmarks.landmark[8].x * width), 
                  int(hand_landmarks.landmark[8].y * height))
            
            # Visualization
            cv2.circle(image, p4, 6, (255, 0, 0), cv2.FILLED)
            cv2.circle(image, p8, 6, (255, 0, 0), cv2.FILLED)
            cv2.line(image, p4, p8, (255, 0, 0), 2)
            
            # Calculate and send distance
            distance = math.dist(p4, p8)
            client.send_message("/line/", distance)
            
            # Draw landmarks
            mp_draw.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2)
            )

    cv2.imshow('Hand Tracking', image)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()