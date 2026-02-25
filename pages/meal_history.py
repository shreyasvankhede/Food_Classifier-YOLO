import streamlit as st

# 🔐 Block access if not logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.switch_page("front.py")
    st.stop()

from calorie_counter import User

user = User(st.session_state.username)

st.title("Today's Meals")

st.write("Breakfast")

st.write("Lunch")

st.write("Snacks")

st.write("Dinner")


