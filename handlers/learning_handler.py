import cv2

from core.landmark_processor import process_landmarks
from core.predictor import predict
from core.smoothing import smooth_prediction

from core.learning_evaluator import evaluate_prediction

class LearningVideoProcessor:

    def __init__(self, learning_engine):
        self.learning_engine = learning_engine

        self.last_prediction = None
        self.last_confidence = 0.0

        self.status = "waiting"
        self.message = "Show the sign."

    def recv(self, frame):

        image = frame.to_ndarray(format="bgr24")

        landmarks = process_landmarks(image)

        if landmarks is None:
            self.status = "waiting"
            self.message = "Show your hand clearly."

            return self._return_frame(image)

        # Existing prediction function
        prediction_result = predict(landmarks)

        predicted_letter = None
        confidence = 0.0

        if prediction_result is not None:

            predicted_letter = prediction_result.get("label")
            confidence = prediction_result.get("confidence", 0.0)

        if predicted_letter is not None:
            predicted_letter = smooth_prediction(predicted_letter)

        self.last_prediction = predicted_letter
        self.last_confidence = confidence

        target_letter = self.learning_engine.current_letter

        if target_letter is not None:

            result = evaluate_prediction(
                target_letter=target_letter,
                predicted_letter=predicted_letter,
                confidence=confidence
            )

            self.status = result["status"]
            self.message = result["message"]

        return self._return_frame(image)

    def _return_frame(self, image):
        return image