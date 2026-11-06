CORRECT_THRESHOLD = 0.85
ALMOST_THRESHOLD = 0.55


def evaluate_prediction(
    target_letter,
    predicted_letter,
    confidence
):
    """
    Evaluate the user's current ASL sign.

    Returns:
        {
            "status": "correct" | "almost" | "wrong",
            "message": str
        }
    """

    if predicted_letter is None:
        return {
            "status": "wrong",
            "message": "No hand detected. Show your hand clearly."
        }

    predicted_letter = predicted_letter.upper()
    target_letter = target_letter.upper()

    if predicted_letter == target_letter:

        if confidence >= CORRECT_THRESHOLD:
            return {
                "status": "correct",
                "message": "Correct!"
            }

        return {
            "status": "almost",
            "message": "Almost there! Hold the sign clearly."
        }

    if confidence < ALMOST_THRESHOLD:
        return {
            "status": "almost",
            "message": "Almost there! Check the reference image."
        }

    return {
        "status": "wrong",
        "message": "That's not quite right. Try again."
    }