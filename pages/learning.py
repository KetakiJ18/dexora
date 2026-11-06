import streamlit as st


LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class LearningEngine:

    def __init__(self):
        self.reset()

    def reset(self):
        self.current_index = 0
        self.completed = False

    @property
    def letters(self):
        return LETTERS

    @property
    def current_letter(self):
        if self.completed:
            return None

        return LETTERS[self.current_index]

    @property
    def progress(self):
        return self.current_index + 1

    @property
    def total_letters(self):
        return len(LETTERS)

    def advance(self):

        if self.completed:
            return

        self.current_index += 1

        if self.current_index >= self.total_letters:
            self.completed = True

    def reset(self):
        self.current_index = 0
        self.completed = False

    def is_complete(self):
        return self.completed


def learning_page():

    st.title("🎓 Learn ASL")

    if "learning_engine" not in st.session_state:
        st.session_state.learning_engine = LearningEngine()

    engine = st.session_state.learning_engine

    if engine.is_complete():

        st.success("🎉 You completed all 26 letters!")

        if st.button("Restart Learning"):
            engine.reset()
            st.rerun()

        return

    st.subheader(
        f"Letter {engine.progress} of {engine.total_letters}"
    )

    st.markdown(
        f"# {engine.current_letter}"
    )

    st.progress(
        engine.progress / engine.total_letters
    )

    if st.button("Next Letter"):
        engine.advance()
        st.rerun()

    if st.button("Restart"):
        engine.reset()
        st.rerun()