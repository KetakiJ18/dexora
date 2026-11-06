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
import time

from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# Core
from core.landmark_processor import process_landmarks
from core.predictor import predict
from core.smoothing import smooth_prediction
from core.word_builder import update_word
import core.word_builder as word_builder

# UI
from ui.display import draw_text, draw_buttons
from ui.buttons import get_hovered_button
from ui.progress import draw_hover_progress

# Game
import game.game_manager as game
from core.word_game import generate_word, check_match

# Handlers
from handlers.gesture_handler import handle_one_hand, handle_two_hands
from gestures.exit_gesture import check_exit

# MediaPipe
import mediapipe as mp


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


# =========================================================
# ASL VIDEO PROCESSOR
# =========================================================

class ASLProcessor(VideoProcessorBase):

    def __init__(self):

        self.hands = mp_hands.Hands(
            max_num_hands=2
        )

        self.final_pred = ""

        self.hover_start = None
        self.hover_target = None

        self.HOVER_TIME = 1.5

        self.cursor_visible = True
        self.last_blink = time.time()

    # =====================================================
    # FRAME PROCESSING
    # =====================================================

    def recv(self, frame):

        img = frame.to_ndarray(format="bgr24")

        # -------------------------------------------------
        # Mirror camera
        # -------------------------------------------------

        img = cv2.flip(img, 1)

        # -------------------------------------------------
        # MediaPipe
        # -------------------------------------------------

        rgb = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2RGB
        )

        results = self.hands.process(rgb)

        # -------------------------------------------------
        # Cursor blink
        # -------------------------------------------------

        if time.time() - self.last_blink > 0.5:

            self.cursor_visible = not self.cursor_visible
            self.last_blink = time.time()

        hovering = None

        # =================================================
        # HAND DETECTION
        # =================================================

        if results.multi_hand_landmarks:

            num_hands = len(
                results.multi_hand_landmarks
            )

            # =================================================
            # ONE HAND
            # =================================================

            if num_hands == 1:

                hand = results.multi_hand_landmarks[0]

                # Draw landmarks
                mp_draw.draw_landmarks(
                    img,
                    hand,
                    mp_hands.HAND_CONNECTIONS
                )

                # ---------------------------------------------
                # Landmark processing
                # ---------------------------------------------

                data = process_landmarks(hand)

                # ---------------------------------------------
                # Prediction
                # ---------------------------------------------

                pred = predict(data)

                # ---------------------------------------------
                # Smoothing
                # ---------------------------------------------

                self.final_pred = smooth_prediction(pred)

                # ---------------------------------------------
                # Word builder / gesture handling
                # ---------------------------------------------

                handle_one_hand(
                    hand,
                    img,
                    self.final_pred,
                    update_word
                )

                # ---------------------------------------------
                # Hover detection
                # ---------------------------------------------

                h, w, _ = img.shape

                hovering = get_hovered_button(
                    hand,
                    w,
                    h
                )

                # =================================================
                # BUTTON HOVER
                # =================================================

                if hovering:

                    if self.hover_target != hovering:

                        self.hover_start = time.time()
                        self.hover_target = hovering

                    elapsed = (
                        time.time()
                        - self.hover_start
                    )

                    # Fingertip position
                    index_tip = hand.landmark[8]

                    cx = int(index_tip.x * w)
                    cy = int(index_tip.y * h)

                    # Draw hover progress
                    draw_hover_progress(
                        img,
                        (cx, cy),
                        elapsed,
                        self.HOVER_TIME
                    )

                    # -----------------------------------------
                    # Button activated
                    # -----------------------------------------

                    if elapsed > self.HOVER_TIME:

                        self.hover_start = None
                        self.hover_target = None

                        # Submit
                        if hovering == "submit":

                            game.submit_word(
                                word_builder.word,
                                check_match
                            )

                            word_builder.word = ""
                            word_builder.cursor_pos = 0

                        # New word
                        elif hovering == "new":

                            game.new_game(
                                generate_word
                            )

                            word_builder.word = ""
                            word_builder.cursor_pos = 0

                else:

                    self.hover_start = None
                    self.hover_target = None

            # =================================================
            # TWO HANDS
            # =================================================

            elif num_hands == 2:

                left_hand = None
                right_hand = None

                # ---------------------------------------------
                # Identify left/right hands
                # ---------------------------------------------

                for i, handedness in enumerate(
                    results.multi_handedness
                ):

                    label = (
                        handedness
                        .classification[0]
                        .label
                    )

                    if label == "Left":

                        left_hand = (
                            results.multi_hand_landmarks[i]
                        )

                    else:

                        right_hand = (
                            results.multi_hand_landmarks[i]
                        )

                # ---------------------------------------------
                # Both hands available
                # ---------------------------------------------

                if left_hand and right_hand:

                    # Draw landmarks
                    mp_draw.draw_landmarks(
                        img,
                        left_hand,
                        mp_hands.HAND_CONNECTIONS
                    )

                    mp_draw.draw_landmarks(
                        img,
                        right_hand,
                        mp_hands.HAND_CONNECTIONS
                    )

                    # -----------------------------------------
                    # Exit gesture
                    # -----------------------------------------

                    exit_flag, exit_elapsed = check_exit(
                        left_hand,
                        right_hand,
                        img
                    )

                    # -----------------------------------------
                    # Exit progress
                    # -----------------------------------------

                    if exit_elapsed > 0:

                        h, w, _ = img.shape

                        lx = int(
                            left_hand.landmark[8].x * w
                        )

                        ly = int(
                            left_hand.landmark[8].y * h
                        )

                        rx = int(
                            right_hand.landmark[8].x * w
                        )

                        ry = int(
                            right_hand.landmark[8].y * h
                        )

                        cx = (lx + rx) // 2
                        cy = (ly + ry) // 2 - 50

                        draw_hover_progress(
                            img,
                            (cx, cy),
                            exit_elapsed,
                            2
                        )

                    # -------------------------------------------------
                    # Streamlit cannot "break" the app like the local
                    # OpenCV loop. We simply stop processing this frame.
                    # -------------------------------------------------

                    if exit_flag:

                        return av.VideoFrame.from_ndarray(
                            img,
                            format="bgr24"
                        )

                    # ---------------------------------------------
                    # Two-hand handler
                    # ---------------------------------------------

                    handle_two_hands(
                        left_hand,
                        right_hand
                    )

        # =================================================
        # UI
        # =================================================

        draw_text(
            img,
            self.final_pred,
            word_builder.word,
            word_builder.cursor_pos,
            game.target_word,
            game.game_result,
            self.cursor_visible
        )

        draw_buttons(
            img,
            hovering
        )

        # =================================================
        # RETURN FRAME
        # =================================================

        return av.VideoFrame.from_ndarray(
            img,
            format="bgr24"
        )


# =========================================================
# WORD GAME PAGE
# =========================================================

def word_game_page():

    st.title("🖐️ ASL Trainer")

    # -----------------------------------------------------
    # Initialize game
    # -----------------------------------------------------

    if "game_initialized" not in st.session_state:

        game.new_game(
            generate_word
        )

        word_builder.word = ""
        word_builder.cursor_pos = 0

        st.session_state.game_initialized = True

    # -----------------------------------------------------
    # Target word
    # -----------------------------------------------------

    st.subheader("🎯 Target Word")

    st.markdown(
        f"# {game.target_word}"
    )

    # -----------------------------------------------------
    # Camera
    # -----------------------------------------------------

    webrtc_streamer(
        key="asl_trainer",
        video_processor_factory=ASLProcessor,
        media_stream_constraints={
            "video": True,
            "audio": False
        },
        async_processing=True
    )

    # -----------------------------------------------------
    # Current word
    # -----------------------------------------------------

    st.subheader("Your Input")

    st.markdown(
        f"### {word_builder.word}"
    )

    # -----------------------------------------------------
    # Game result
    # -----------------------------------------------------

    if game.game_result:

        if game.game_result == "correct":

            st.success("🎉 Correct!")

        elif game.game_result == "incorrect":

            st.error("❌ Try again!")

    # -----------------------------------------------------
    # Streamlit fallback controls
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Submit",
            use_container_width=True
        ):

            game.submit_word(
                word_builder.word,
                check_match
            )

            word_builder.word = ""
            word_builder.cursor_pos = 0

            st.rerun()

    with col2:

        if st.button(
            "New Word",
            use_container_width=True
        ):

            game.new_game(
                generate_word
            )

            word_builder.word = ""
            word_builder.cursor_pos = 0

            st.rerun()


# =========================================================
# MAIN APP
# =========================================================

st.set_page_config(
    page_title="ASL Trainer",
    page_icon="🖐️",
    layout="wide"
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🖐️ ASL Trainer")

page = st.sidebar.radio(
    "Choose Mode",
    [
        "🎯 Word Game"
    ]
)


# =========================================================
# PAGE ROUTING
# =========================================================

if page == "🎯 Word Game":

    word_game_page()