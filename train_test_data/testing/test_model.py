import cv2
import mediapipe as mp
import joblib
import numpy as np
from collections import deque, Counter
import math, time

exit_start = None
EXIT_HOLD_TIME = 1.2
EXIT_DISTANCE = 40
final_pred = ""

prediction_buffer = deque(maxlen=10)

model = joblib.load("models\\asl_model.pkl")

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

while True:

    success, frame = cap.read()
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:

        num_hands = len(results.multi_hand_landmarks)

        if num_hands == 1:

            hand = results.multi_hand_landmarks[0]

            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            lm = hand.landmark
            coords = []

            for point in lm:
                coords.append([point.x, point.y, point.z])

            coords = np.array(coords)

            wrist = coords[0]
            coords = coords - wrist

            max_value = np.max(np.abs(coords))

            if max_value != 0:
                coords = coords / max_value

            data = coords.flatten().reshape(1, -1)

            prediction = model.predict(data)[0]

            prediction_buffer.append(prediction)

            if len(prediction_buffer) == 10:
                final_pred = Counter(prediction_buffer).most_common(1)[0][0]

            cv2.putText(
                frame,
                f"Letter: {final_pred}",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0,255,0),
                3
            )

        elif num_hands == 2:

            left_hand = None
            right_hand = None

            for i, handedness in enumerate(results.multi_handedness):
                label = handedness.classification[0].label

                if label == "Left":
                    left_hand = results.multi_hand_landmarks[i]
                else:
                    right_hand = results.multi_hand_landmarks[i]

            mp_draw.draw_landmarks(frame, left_hand, mp_hands.HAND_CONNECTIONS)
            mp_draw.draw_landmarks(frame, right_hand, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape

            if left_hand and right_hand:

                x1 = int(left_hand.landmark[8].x * w)
                y1 = int(left_hand.landmark[8].y * h)

                x2 = int(right_hand.landmark[8].x * w)
                y2 = int(right_hand.landmark[8].y * h)

            dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            cv2.line(frame, (x1, y1), (x2, y2), (0,255,255), 2)

            if dist < EXIT_DISTANCE:
                if exit_start is None:
                    exit_start = time.time()

                elapsed = time.time() - exit_start

                cv2.putText(
                    frame,
                    f"EXIT GESTURE DETECTED: {elapsed:.1f}s",
                    (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0,0,255),
                    3
                )

                if elapsed > EXIT_HOLD_TIME:
                    break
            else:
                exit_start = None

    cv2.imshow("ASL Prediction", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()