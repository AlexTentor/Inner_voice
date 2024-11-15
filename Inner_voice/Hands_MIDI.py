import cv2
import math
import mediapipe as mp
from pythonosc import udp_client
import mido
import numpy as np

# MIDI utilities
def clamp_and_scale(value, min_value=100, max_value=800, midi_min=0, midi_max=127):
    clamped_value = max(min_value, min(max_value, value))
    scaled_value = midi_min + (clamped_value - min_value) / (max_value - min_value) * (midi_max - midi_min)
    return int(scaled_value)

# MIDI Setup
out_port = mido.open_output("to Max 1")

# OSC Setup
IP_local = "127.0.0.1"
OSC_port = 7400
client = udp_client.SimpleUDPClient(IP_local, OSC_port)

# Video input and output setup
input_video_path = "/Users/alextentor/Downloads/Hands of Bresson.mp4"  # Replace with your input video path
output_video_path = "/Users/alextentor/Downloads/Hands of Bresson_modified.mp4"  # Replace with your desired output path

vid = cv2.VideoCapture(0)
fps = int(vid.get(cv2.CAP_PROP_FPS))
width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

mphands = mp.solutions.hands
Hands = mphands.Hands(max_num_hands=1, min_detection_confidence=0.2, min_tracking_confidence=0.2)
mpdraw = mp.solutions.drawing_utils

finger_state = {}
fingers_ids = np.array([0, 4, 8, 12, 16, 20])
threshold = 200

while True:
    ret, frame = vid.read()
    if not ret:
        break

    RGBframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = Hands.process(RGBframe)
    if result.multi_hand_landmarks:
        print("hand found")
        for handLm in result.multi_hand_landmarks:
            mpdraw.draw_landmarks(frame, handLm, mphands.HAND_CONNECTIONS,
                                  mpdraw.DrawingSpec(color=(200, 200, 200), circle_radius=7, thickness=cv2.FILLED),
                                  mpdraw.DrawingSpec(color=(200, 200, 200), thickness=3))
            
            h, w, _ = frame.shape
            distances = []
            
            for i in [8, 12, 16, 20]:
                x1, y1 = int(handLm.landmark[i].x * w), int(handLm.landmark[i].y * h)
                x2, y2 = int(handLm.landmark[4].x * w), int(handLm.landmark[4].y * h)

                distance = int(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
                distances.append(distance)
                
                if distance >= threshold: 
                    if i not in finger_state or not finger_state[i]:
                        dedo = int((i-4)/4)
                        msg = mido.Message('note_on', note=dedo + 36)
                        out_port.send(msg)
                        print(f"{dedo}: ON")
                        finger_state[i] = True
                else: 
                    if i in finger_state and finger_state[i]:
                        dedo = int((i-4)/4)
                        msg = mido.Message('note_off', note=dedo + 36)
                        out_port.send(msg)
                        finger_state[i] = False

            print("Distances:", distances)

            for distance in distances:
                client.send_message("/distances/", distance)

            for i, distance in enumerate(distances):
                midi_value = clamp_and_scale(distance, min_value=0, max_value=1000, midi_min=0, midi_max=127)
                cc_message = mido.Message('control_change', channel=0, control=i, value=midi_value)
                out_port.send(cc_message)

            if 4 in handLm.landmark and 8 in handLm.landmark:
                Tx, Ty = int(handLm.landmark[4].x * w), int(handLm.landmark[4].y * h)
                Ix, Iy = int(handLm.landmark[8].x * w), int(handLm.landmark[8].y * h)
                cv2.circle(frame, (Tx, Ty), 6, (255, 0, 0), cv2.FILLED)
                cv2.circle(frame, (Ix, Iy), 6, (255, 0, 0), cv2.FILLED)
                cv2.line(frame, (Ix, Iy), (Tx, Ty), (255, 0, 0), 5)
                line_value = math.dist((Ix, Iy), (Tx, Ty))
                client.send_message("/line/", line_value)
                midi_value = clamp_and_scale(line_value, min_value=0, max_value=300, midi_min=0, midi_max=127)
                cc_message = mido.Message('control_change', channel=0, control=1, value=midi_value)
                out_port.send(cc_message)
                print("Outport CC sent, value", midi_value)

    out.write(frame)
    cv2.imshow("video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
out.release()
cv2.destroyAllWindows()