
import streamlit as st
from calorie_counter import User

# -------------------------
# 🔐 Require Login
# -------------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.switch_page("front.py")
    st.stop()

user = User(st.session_state.username)
st.title("Log food")
# =========================================================
# (Search + Camera Button)
# =========================================================

col_search, col_cam = st.columns([5, 1])

with col_search:
    search_query = st.text_input(
        "",
        placeholder="Search food (e.g. dosa, paneer, idli...)",
        label_visibility="collapsed"
    )

with col_cam:
    if st.button("📷", use_container_width=True):
        st.session_state.camera_open = True

# =========================================================
# 📷 CAMERA MODE
# =========================================================

image_source = None

if st.session_state.get("camera_open", False):
    camera_image = st.camera_input("Take a picture")

    if camera_image:
        image_source = camera_image
        st.image(camera_image, use_container_width=True)

        with st.spinner("Detecting food..."):
            result = user.detect_food(image_source)

        if result:
            class_counts, detected_names = result

            if len(detected_names) > 0:
                st.write("Confirm detected foods")

                confirmed_items = []

                for idx, food in enumerate(class_counts.keys()):
                    suggestions = user.suggest_similar_foods(food)

                    corrected = st.selectbox(
                        f"{food}",
                        suggestions,
                        key=f"cam_name_{idx}"
                    )

                    qty = st.number_input(
                        "grams",
                        min_value=1,
                        max_value=1000,
                        value=100,
                        key=f"cam_qty_{idx}"
                    )

                    confirmed_items.append((corrected, qty))

                if st.button("Add Detected Meal"):
                    meal_id = user.create_meal()

                    for food, qty in confirmed_items:
                        user.add_food_to_meal(meal_id, food, qty)

                    st.success("Meal logged successfully!")
                    st.session_state.camera_open = False

            else:
                st.warning("No food detected.")

# =========================================================
# 🔎 LIVE SEARCH MODE
# =========================================================

selected_food = None

if search_query:
    matches = user.suggest_similar_foods(search_query)

    if matches:
        selected_food = st.selectbox(
            "",
            matches,
            label_visibility="collapsed"
        )
    else:
        st.warning("No matching foods found.")
if selected_food is not None:
    qty = st.number_input(
    "",
    min_value=1,
    max_value=1000,
    value=100,
    label_visibility="collapsed"
 )

# Maintain active meal session
    if "manual_meal_id" not in st.session_state:
     st.session_state.manual_meal_id = None

    if st.button("Add Food"):
        if selected_food:
            if st.session_state.manual_meal_id is None:
                st.session_state.manual_meal_id = user.create_meal()

            user.add_food_to_meal(st.session_state.manual_meal_id, selected_food, qty)
            st.success(f"{selected_food} added!")

# =========================================================
# ✅ FINISH MEAL
# =========================================================

if st.session_state.manual_meal_id:
    if st.button("Finish Meal"):
        meal_id = st.session_state.manual_meal_id

        calories, carbs, protein, fats, fibre, sugar = user.calculate_meal_cals(meal_id)

        st.subheader("Meal Summary")
        st.metric("Calories", f"{calories:.2f} kcal")
        st.write(f"Carbs: {carbs:.2f} g")
        st.write(f"Protein: {protein:.2f} g")
        st.write(f"Fats: {fats:.2f} g")
        st.write(f"Fibre: {fibre:.2f} g")
        st.write(f"Sugar: {sugar:.2f} g")

        st.session_state.manual_meal_id = None
