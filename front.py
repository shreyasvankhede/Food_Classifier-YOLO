import streamlit as st
from Auth import AuthManager
from calorie_counter import User

auth=AuthManager()


if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
if "username" not in st.session_state:
    st.session_state.username = None


st.title("AI Calorie tracker")

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u=st.text_input("",placeholder="Username")
        p=st.text_input("",placeholder="Password",type="password")

        if st.button("Login"):
            if auth.login(u,p):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.success("Logged in")
                st.rerun()
            else:
                st.error("Invalid credentials")
    with tab2:
        u = st.text_input("",placeholder="Username",key="reg_name")
        p = st.text_input("",placeholder="Password", type="password",key="reg_pass")

        if st.button("Register"):
            if auth.register(u, p):
                st.success("User created")
            else:
                st.error("User already exists")
else:
    st.success(f"Welcome {st.session_state.username}")
    user = User(st.session_state.username)
    st.switch_page("pages/Food_Detection.py")
