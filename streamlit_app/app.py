import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import streamlit as st
import av
import cv2
import random

from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# Learning page

# Existing modules
from core.landmark_processor import process_landmarks
from core.predictor import predict
from core.smoothing import smooth_prediction
from core.word_builder import update_word
import core.word_builder as word_builder

from handlers.gesture_handler import handle_one_hand

import mediapipe as mp


mp_hands = mp.solutions.hands


# =========================================================
# WORD GAME VIDEO PROCESSOR
# =========================================================

class ASLProcessor(VideoProcessorBase):

    def __init__(self):
        self.hands = mp_hands.Hands(max_num_hands=1)
        self.prev_pred = ""

    def recv(self, frame):

        img = frame.to_ndarray(format="bgr24")

        # Mirror camera
        img = cv2.flip(img, 1)

        rgb = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )

        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:

            hand = results.multi_hand_landmarks[0]

            # Existing landmark processing
            data = process_landmarks(hand)

            # Existing prediction
            pred = predict(data)

            # Existing smoothing
            final_pred = smooth_prediction(pred)

            # Existing word builder
            handle_one_hand(
                hand,
                img,
                final_pred,
                update_word
            )

            # Draw landmarks
            mp.solutions.drawing_utils.draw_landmarks(
                img,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

        return av.VideoFrame.from_ndarray(
            img,
            format="bgr24"
        )


# =========================================================
# WORD GAME
# =========================================================

def word_game_page():

    st.title("🎯 ASL Word Game")

    # ---------------------------------------------
    # Target word
    # ---------------------------------------------

    if "target_word" not in st.session_state:
        st.session_state.target_word = "HELLO"

    st.subheader("Target")

    st.markdown(
        f"### {st.session_state.target_word}"
    )

    # ---------------------------------------------
    # Camera
    # ---------------------------------------------

    webrtc_streamer(
        key="asl_word_game",
        video_processor_factory=ASLProcessor,
        media_stream_constraints={
            "video": True,
            "audio": False
        }
    )

    # ---------------------------------------------
    # User's generated word
    # ---------------------------------------------

    st.subheader("Your Input")

    st.markdown(
        f"### {word_builder.word}"
    )

    # ---------------------------------------------
    # Game controls
    # ---------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Submit",
            use_container_width=True
        ):

            if (
                word_builder.word
                == st.session_state.target_word
            ):

                st.success("🎉 Correct!")

            else:

                st.error("❌ Try again!")

    with col2:

        if st.button(
            "New Word",
            use_container_width=True
        ):

            words = [
                "APPLE",
                "TRAIN",
                "WORLD",
                "HELLO"
            ]

            st.session_state.target_word = (
                random.choice(words)
            )

            word_builder.word = ""

            st.rerun()


# =========================================================
# MAIN APP
# =========================================================

st.set_page_config(
    page_title="ASL Trainer",
    page_icon="🖐️",
    layout="wide"
)


# ---------------------------------------------------------
# Navigation
# ---------------------------------------------------------

st.sidebar.title("🖐️ ASL Trainer")

page = st.sidebar.radio(
    "Choose Mode",
    [
        "🎓 Learn ASL",
        "🎯 Word Game"
    ]
)


# =========================================================
# PAGE ROUTING
# =========================================================

if page == "🎓 Learn ASL":

    learning_page()


elif page == "🎯 Word Game":

    word_game_page()
