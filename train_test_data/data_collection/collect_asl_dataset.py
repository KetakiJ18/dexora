import cv2
import mediapipe as mp
import csv
import os
import time
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

DATA_PATH = r"dataset\\asl_landmarks.csv"

if not os.path.exists(DATA_PATH):
    with open(DATA_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["label"]
        for i in range(21):
            header += [f"x{i}", f"y{i}", f"z{i}"]
        writer.writerow(header)

sample_count = {}

pinch_start = None
PINCH_THRESHOLD = 0.05
HOLD_TIME = 2.5


def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


while True:

    success, frame = cap.read()
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    label_to_save = None

    if results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            lm = hand.landmark


            row = []

            for point in lm:
                row.extend([point.x, point.y, point.z])


            thumb = lm[4]
            index = lm[8]

            pinch_dist = distance(thumb, index)

            if pinch_dist < PINCH_THRESHOLD:

                if pinch_start is None:
                    pinch_start = time.time()

                elapsed = time.time() - pinch_start

                cv2.putText(frame,
                            f"Pinch exit: {elapsed:.1f}s",
                            (20,120),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0,0,255),
                            2)

                if elapsed > HOLD_TIME:
                    print("Exiting data collection")
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

            else:
                pinch_start = None


    key = cv2.waitKey(1) & 0xFF

    if key >= ord('a') and key <= ord('z'):
        label_to_save = chr(key).upper()

    if label_to_save and results.multi_hand_landmarks:

        for hand in results.multi_hand_landmarks:

            lm = hand.landmark
            row = []

            for point in lm:
                row.extend([point.x, point.y, point.z])

            data_row = [label_to_save] + row

            with open(DATA_PATH, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(data_row)

            sample_count[label_to_save] = sample_count.get(label_to_save, 0) + 1

            print(f"Saved {label_to_save} sample {sample_count[label_to_save]}")


    y = 40
    for letter in sorted(sample_count.keys()):
        text = f"{letter}: {sample_count[letter]}"
        cv2.putText(frame,
                    text,
                    (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,255,0),
                    2)
        y += 25

    cv2.putText(frame,
                "Press A-Z to save sample",
                (20,420),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255,255,255),
                2)

    cv2.imshow("ASL Dataset Collector", frame)

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()