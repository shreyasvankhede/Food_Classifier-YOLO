import streamlit as st
from calorie_counter import User
from navbar import render_navbar

# =========================================================
# Page Config
# =========================================================
st.set_page_config(layout="wide")

# Controlled width + smaller fonts
st.markdown("""
<style>
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}

[data-testid="stMetricLabel"] {
    font-size: 14px !important;
}
[data-testid="stMetricValue"] {
    font-size: 20px !important;
}
p {
    font-size: 14px;
}
h3 {
    font-size: 20px !important;
}
h2 {
    font-size: 24px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 🔐 Require Login
# =========================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.switch_page("front.py")
    st.stop()



render_navbar()
st.divider()

if "camera_open" not in st.session_state:
    st.session_state.camera_open = False

user = User(st.session_state.username)

# =========================================================
# TITLE
# =========================================================
st.title("Log Food")

# =========================================================
# SEARCH + CAMERA
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
# CAMERA MODE (Camera + Upload)
# =========================================================
if st.session_state.camera_open:

    st.markdown("### Scan Food")

    # 🔴 Close Scanner Button
    if st.button("Close Scanner"):
        st.session_state.camera_open = False
        st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        camera_image = st.camera_input("Take a picture")

    with col2:
        uploaded_image = st.file_uploader(
            "Or upload an image",
            type=["jpg", "jpeg", "png"]
        )

    image_to_process = None

    if camera_image:
        image_to_process = camera_image
    elif uploaded_image:
        image_to_process = uploaded_image

    if image_to_process:

        st.image(image_to_process, use_container_width=True)

        with st.spinner("Detecting food..."):
            result = user.detect_food(image_to_process)

        if result:
            class_counts, detected_names = result

            if class_counts:

                st.markdown("### Confirm & Adjust Detected Foods")

                confirmed_items = []

                meal_type = st.selectbox(
                    "Select Meal",
                    ("Breakfast", "Lunch", "Dinner", "Snacks"),
                    index=None,
                    placeholder="Choose meal type"
                )

                st.divider()

                for idx, food in enumerate(set(detected_names)):

                  
                    st.markdown(f"**Detected:** {food}")

                    suggestions = user.suggest_similar_foods(food)

                    colA, colB = st.columns([3, 1.5])

                    with colA:
                        corrected = st.selectbox(
                            "Food Name",
                            suggestions if suggestions else [food],
                            key=f"cam_name_{idx}"
                        )

                    with colB:
                        qty = st.number_input(
                            "Quantity (g)",
                            min_value=1,
                            max_value=1000,
                            value=100,   
                            key=f"cam_qty_{idx}"
                        )

                    confirmed_items.append((corrected, qty))
                    st.divider()

                if st.button("Add Detected Meal", use_container_width=True):

                    if not meal_type:
                        st.warning("Please select meal type")
                    else:
                        for food, qty in confirmed_items:
                            user.add_food_to_meal(meal_type, food, qty)

                        st.success("Meal logged successfully!")
                        st.session_state.camera_open = False
                        st.rerun()

            else:
                st.warning("No food detected.")

        else:
            st.warning("Detection failed.")

# =========================================================
# SEARCH MODE
# =========================================================
col_food, col_qty, col_meal = st.columns([4, 1.5, 2])

selected_food = None
qty = None
meal_type = None

if search_query:

    matches = user.suggest_similar_foods(search_query)

    if matches:

        with col_food:
            selected_food = st.selectbox(
                "",
                matches,
                label_visibility="collapsed"
            )

        with col_qty:
            qty = st.number_input(
                "Qty (g)",
                min_value=1.0,
                max_value=1000.0,
                value=100.0
            )

        with col_meal:
            meal_type = st.selectbox(
                "Meal",
                ("Breakfast", "Lunch", "Dinner", "Snacks"),
                index=None,
                placeholder="Select"
            )
    else:
        st.warning("No matching foods found.")

# =========================================================
# NUTRITION SUMMARY
# =========================================================
if selected_food:

    nutrition = user.get_food_info(selected_food)

    if nutrition:
        calories, carbs, protein, fats, sugar, fibre = nutrition

        st.markdown("### Nutrition (per 100g)")

        c1, c2, c3 = st.columns(3)
        c1.metric("Calories", f"{calories:.0f} kcal")
        c2.metric("Carbs", f"{carbs:.1f} g")
        c3.metric("Protein", f"{protein:.1f} g")

        c4, c5, c6 = st.columns(3)
        c4.metric("Fats", f"{fats:.1f} g")
        c5.metric("Fibre", f"{fibre:.1f} g")
        c6.metric("Sugar", f"{sugar:.1f} g")

        if st.button("Add Food"):
            if meal_type:
                user.add_food_to_meal(meal_type, selected_food, qty)
                st.success(f"{selected_food} added!")
            else:
                st.warning("Please select meal type")

# =========================================================
# LOGGED MEALS
# =========================================================
st.divider()
st.header("Logged Meals")

daily_macros = user.calculate_daily_macros()
daily_cal = daily_macros[0]
st.metric("Today's Total Calories", f"{daily_cal:.0f} kcal")

# =========================================================
# Meal Renderer
# =========================================================
def render_meal_section(meal_name):

    st.markdown(f"### {meal_name}")

    meal_cals = user.calculate_meal_cals(meal_name)
    st.metric(f"{meal_name} Calories", f"{meal_cals[0]:.0f} kcal")

    df = user.get_meal_entries(meal_name)

    if df.empty:
        st.info("No entries logged.")
        return

    # Keep full copy for comparison
    original_df = df.copy()

    # Rename columns for UI (DO NOT drop item_id)
    df = df.rename(columns={
        "dish_name": "Food",
        "quantity_g": "Quantity (g)",
        "calories": "Calories",
        "carbs": "Carbs (g)",
        "protein": "Protein (g)",
        "fats": "Fats (g)",
        "fibre": "Fibre (g)",
        "sugar": "Sugar (g)"
    })

    # Add serial number column (for display only)
    df = df.reset_index(drop=True)
    df.insert(0, "Sr No", df.index + 1)

    # Data editor
    edited_df = st.data_editor(
        df,
        column_config={
            "item_id": None,  # 🔥 Hide ID visually but keep internally
            "Sr No": st.column_config.NumberColumn("Sr", disabled=True, width="xxsmall"),
            "Food": st.column_config.TextColumn("Food", disabled=True),
            "Quantity (g)": st.column_config.NumberColumn("Qty (g)"),
            "Calories": st.column_config.NumberColumn("Cal", disabled=True),
            "Carbs (g)": st.column_config.NumberColumn("Carb", disabled=True),
            "Protein (g)": st.column_config.NumberColumn("Pro", disabled=True),
            "Fats (g)": st.column_config.NumberColumn("Fat", disabled=True),
            "Fibre (g)": st.column_config.NumberColumn("Fib", disabled=True),
            "Sugar (g)": st.column_config.NumberColumn("Sug", disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="delete",
        key=f"{meal_name}_editor"
    )

    # =====================================================
    # DELETE LOGIC (Robust)
    # =====================================================
    original_ids = set(original_df["item_id"])
    edited_ids = set(edited_df["item_id"])

    deleted_ids = original_ids - edited_ids

    if deleted_ids:
        for item_id in deleted_ids:
            user.change_entry(item_id, delete_entry=True)
        st.rerun()

    # =====================================================
    # UPDATE LOGIC (Quantity Change)
    # =====================================================
    for _, row in edited_df.iterrows():

        item_id = row["item_id"]

        original_row = original_df[
            original_df["item_id"] == item_id
        ].iloc[0]

        if row["Quantity (g)"] != original_row["quantity_g"]:
            user.change_entry(
                item_id,
                new_quantity=row["Quantity (g)"]
            )
            st.rerun()

render_meal_section("Breakfast")
render_meal_section("Lunch")
render_meal_section("Snacks")
render_meal_section("Dinner")