import streamlit as st
from calorie_counter import User
from datetime import datetime

 
# Page Config
 
st.set_page_config(layout="wide")

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
    font-size: 22px !important;
}
.macro-label {
    font-size: 13px;
    color: #888;
    margin-bottom: 2px;
}
.macro-row {
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

 
# 🔐 Require Login
 
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.switch_page("front.py")
    st.stop()

username = st.session_state.username
user = User(username)

from navbar import render_navbar

render_navbar()
st.divider()

 
# TITLE
 
st.subheader("Reports")

 
# DATE SELECTOR
 
col1, col2 = st.columns([3, 2])

with col1:
    selected_date = st.date_input(
        "Select Date",
        value=datetime.today()
    )

selected_date = selected_date.strftime("%Y-%m-%d")

 
# DAILY CALORIES
 
daily_macros = user.calculate_daily_macros(date=selected_date)
consumed         = daily_macros[0] or 0  
consumed_carbs   = daily_macros[1] or 0  
consumed_protein = daily_macros[2] or 0 
consumed_fats    = daily_macros[3] or 0  

 
# PROFILE + GOAL
 
profile = user.get_profile_details(username)

if profile:
    age, gender, weight, height, activity = profile

    if gender.lower() == "male":
        bmr = 10*weight + 6.25*height - 5*age + 5
    else:
        bmr = 10*weight + 6.25*height - 5*age - 161

    activity_map = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725
    }

    tdee = bmr * activity_map.get(activity, 1.2)
    remaining = tdee - consumed

    # ── Macro targets ──────────────────────────────────────
    # Protein: 1.6 g per kg bodyweight (general fitness recommendation)
    # Carbs:   ~50 % of TDEE  → kcal / 4
    # Fats:    ~25 % of TDEE  → kcal / 9
    protein_goal = weight * 1.6
    carbs_goal   = (tdee * 0.50) / 4
    fats_goal    = (tdee * 0.25) / 9

     
    # DAILY SUMMARY
     
    st.markdown("## Daily Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Calorie Goal", f"{tdee:.0f} kcal")
    c2.metric("Consumed", f"{consumed:.0f} kcal")
    c3.metric("Remaining", f"{remaining:.0f} kcal")

    cal_progress = min(consumed / tdee, 1.0) if tdee > 0 else 0
    st.progress(cal_progress)

    st.divider()

     
    # MACRO REQUIREMENTS & PROGRESS
     
    st.markdown("## Macro Breakdown")
    st.caption(
        f"Targets based on your profile — **{weight} kg**, "
        f"**{age} yrs**, **{gender.title()}**, "
        f"**{activity.title()}** activity level."
    )

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown("#### 🥩 Protein")
        st.metric(
            label="Goal",
            value=f"{protein_goal:.0f} g",
            delta=f"{consumed_protein - protein_goal:+.0f} g"
        )
        prot_pct = min(consumed_protein / protein_goal, 1.0) if protein_goal > 0 else 0
        st.progress(prot_pct)
        st.caption(f"Consumed: **{consumed_protein:.1f} g** / {protein_goal:.0f} g")

    with m2:
        st.markdown("#### 🍚 Carbohydrates")
        st.metric(
            label="Goal",
            value=f"{carbs_goal:.0f} g",
            delta=f"{consumed_carbs - carbs_goal:+.0f} g"
        )
        carb_pct = min(consumed_carbs / carbs_goal, 1.0) if carbs_goal > 0 else 0
        st.progress(carb_pct)
        st.caption(f"Consumed: **{consumed_carbs:.1f} g** / {carbs_goal:.0f} g")

    with m3:
        st.markdown("#### 🫒 Fats")
        st.metric(
            label="Goal",
            value=f"{fats_goal:.0f} g",
            delta=f"{consumed_fats - fats_goal:+.0f} g"
        )
        fat_pct = min(consumed_fats / fats_goal, 1.0) if fats_goal > 0 else 0
        st.progress(fat_pct)
        st.caption(f"Consumed: **{consumed_fats:.1f} g** / {fats_goal:.0f} g")

else:
    st.warning("Complete your profile to calculate calorie goal.")

st.divider()

 
# ADD FOOD SECTION (Compact)
 
st.markdown(f"### Add Food for {selected_date}")

col_food, col_qty, col_meal, col_btn = st.columns([4, 1.5, 2, 1])

search_query = None
selected_food = None
qty = None
meal_type = None

with col_food:
    search_query = st.text_input(
        "",
        placeholder="Search food...",
        label_visibility="collapsed",
        key=f"report_search_{selected_date}"
    )

if search_query:
    matches = user.suggest_similar_foods(search_query)

    if matches:

        with col_food:
            selected_food = st.selectbox(
                "",
                matches,
                label_visibility="collapsed",
                key=f"report_select_{selected_date}"
            )

        with col_qty:
            qty = st.number_input(
                "g",
                min_value=1.0,
                max_value=1000.0,
                value=100.0,
                key=f"report_qty_{selected_date}"
            )

        with col_meal:
            meal_type = st.selectbox(
                "Meal",
                ("Breakfast", "Lunch", "Dinner", "Snacks"),
                index=None,
                key=f"report_meal_{selected_date}"
            )

        with col_btn:
            if st.button("Add", key=f"report_add_{selected_date}"):

                if meal_type:
                    user.add_food_to_meal(
                        meal_type,
                        selected_food,
                        qty,
                        date=selected_date
                    )
                    st.success("Food added")
                    st.rerun()
                else:
                    st.warning("Select meal")

st.divider()

 
# RENDER MEALS (Editable)
 
def render_meal_section(meal_name):

    st.markdown(f"### {meal_name}")

    meal_cals = user.calculate_meal_cals(meal_name, date=selected_date)
    st.metric(f"{meal_name} Calories", f"{meal_cals[0] or 0:.0f} kcal")

    df = user.get_meal_entries(meal_name, date=selected_date)

    if df.empty:
        st.info("No entries logged.")
        return

    original_df = df.copy()

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

    df = df.reset_index(drop=True)
    df.insert(0, "Sr No", df.index + 1)

    edited_df = st.data_editor(
        df,
        column_config={
            "item_id": None,
            "Sr No": st.column_config.NumberColumn("Sr", disabled=True),
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
        key=f"{meal_name}_{selected_date}"
    )

    # DELETE LOGIC
    original_ids = set(original_df["item_id"])
    edited_ids = set(edited_df["item_id"])
    deleted_ids = original_ids - edited_ids

    if deleted_ids:
        for item_id in deleted_ids:
            user.change_entry(item_id, delete_entry=True)
        st.rerun()

    # UPDATE LOGIC
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