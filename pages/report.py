import streamlit as st

# 🔐 Block access if not logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    
    st.switch_page("front.py")
    st.stop()

import Auth

user = Auth(st.session_state.username)