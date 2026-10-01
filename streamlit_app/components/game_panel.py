import streamlit as st

def render_game_panel():

    st.subheader("🎯 Current Challenge")

    if "target_word" not in st.session_state:
        st.session_state.target_word = "HELLO"

    if "current_word" not in st.session_state:
        st.session_state.current_word = ""

    st.markdown(f"### Target: `{st.session_state.target_word}`")
    st.markdown(f"### Your Input: `{st.session_state.current_word}`")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Submit"):
            if st.session_state.current_word == st.session_state.target_word:
                st.success("Correct!")
            else:
                st.error("Try again!")

    with col2:
        if st.button("🔄 New Word"):
            import random
            words = ["APPLE", "TRAIN", "WORLD", "SMART"]
            st.session_state.target_word = random.choice(words)
            st.session_state.current_word = ""