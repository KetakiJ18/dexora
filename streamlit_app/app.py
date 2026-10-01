import streamlit as st
import av
import cv2

from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# your existing modules
from core.landmark_processor import process_landmarks
from core.predictor import predict
from core.smoothing import smooth_prediction
from core.word_builder import update_word
import core.word_builder as word_builder

from handlers.gesture_handler import handle_one_hand

import mediapipe as mp

mp_hands = mp.solutions.hands


# -------------------------
# VIDEO PROCESSOR
# -------------------------
class ASLProcessor(VideoProcessorBase):

    def __init__(self):
        self.hands = mp_hands.Hands(max_num_hands=1)
        self.prev_pred = ""

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        img = cv2.flip(img, 1)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:

            hand = results.multi_hand_landmarks[0]

            data = process_landmarks(hand)
            pred = predict(data)
            final_pred = smooth_prediction(pred)

            handle_one_hand(hand, img, final_pred, update_word)

            # draw landmarks
            mp.solutions.drawing_utils.draw_landmarks(
                img, hand, mp_hands.HAND_CONNECTIONS
            )

        return av.VideoFrame.from_ndarray(img, format="bgr24")

st.title("🖐️ ASL Trainer")

webrtc_streamer(
    key="asl",
    video_processor_factory=ASLProcessor
)

st.subheader("🎯 Game")

if "target_word" not in st.session_state:
    st.session_state.target_word = "HELLO"

st.markdown(f"Target: {st.session_state.target_word}")
st.markdown(f"Your Input: {word_builder.word}")

col1, col2 = st.columns(2)

with col1:
    if st.button("Submit"):
        if word_builder.word == st.session_state.target_word:
            st.success("Correct!")
        else:
            st.error("Try again!")

with col2:
    if st.button("New Word"):
        import random
        words = ["APPLE", "TRAIN", "WORLD"]
        st.session_state.target_word = random.choice(words)
        word_builder.word = ""