import streamlit as st


def initialize_quiz_state():
    if "quiz_question_index" not in st.session_state:
        st.session_state.quiz_question_index = 0
    
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False


def reset_quiz_state():
    st.session_state.quiz_question_index = 0
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False