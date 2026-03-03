import streamlit as st
from Auth import AuthManager
from calorie_counter import User

auth = AuthManager()

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "Name" not in st.session_state:
    st.session_state.Name=None

if "username" not in st.session_state:
    st.session_state.username = None

# ---------------- AUTO REDIRECT ----------------
if st.session_state.logged_in:
    st.switch_page("pages/Food_Detection.py")
    st.stop()

st.title("AI Calorie Tracker")

tab1, tab2 = st.tabs(["Login", "Register"])

# =========================================================
# LOGIN
# =========================================================
with tab1:

    u = st.text_input("Username", key="login_user")
    p = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):

        if auth.login(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            user = User(u)
            st.session_state.Name=user.get_name()
            st.switch_page("pages/Food_Detection.py")
        else:
            st.error("Invalid credentials")

# =========================================================
# REGISTER
# =========================================================
with tab2:

    st.subheader("Create Account")

    u = st.text_input("Username", key="reg_name")
    p = st.text_input("Password", type="password", key="reg_pass")
    confirm_p = st.text_input("Confirm Password", type="password", key="C_reg_pass")

    st.markdown("### Profile Details")
    Name=st.text_input("Name")
    age = st.number_input("Age", min_value=10, max_value=100, step=1)
    gender = st.selectbox("Gender", ("Male", "Female"))
    weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0)
    height = st.number_input("Height (cm)", min_value=120.0, max_value=220.0)
    activity = st.selectbox(
        "Activity Level",
        ("sedentary", "light", "moderate", "active")
    )

    if p and confirm_p and p != confirm_p:
        st.warning("Passwords do not match")

    if st.button("Register"):

        if not u or not p:
            st.error("Please fill all fields")

        elif p != confirm_p:
            st.error("Passwords do not match")

        else:
            if auth.register(u, p):

                user = User(u)
                user.add_profile_details(
                    Name,
                    age,
                    gender,
                    weight,
                    height,
                    activity
                )

                st.session_state.logged_in = True
                st.session_state.username = u
                user = User(u)
                st.session_state.Name=user.get_name()
                st.switch_page("pages/Food_Detection.py")

            else:
                st.error("User already exists")
