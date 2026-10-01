import streamlit as st

def render_stats():

    st.subheader("📊 Stats")

    if "score" not in st.session_state:
        st.session_state.score = 0

    st.metric("Score", st.session_state.score)