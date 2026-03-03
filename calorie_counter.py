import sqlite3
from rapidfuzz import process, fuzz
from PIL import Image
from ultralytics import YOLO
from collections import Counter
from datetime import datetime
import hashlib
import pandas as pd


# -------------------------
# GLOBAL CONFIG
# -------------------------
DB_PATH = "data/food_db.sqlite"

# Load model ONLY once
MODEL = YOLO("model/best.pt")

DATE = datetime.now().strftime("%Y-%m-%d")


class MealType:
    BREAKFAST = 0
    LUNCH = 1
    DINNER = 2
    SNACKS = 3


# -------------------------
# USER CLASS = CALORIE TRACKER ENGINE
# -------------------------
class User:
    
    def __init__(self, username):
        self.username = username
        self.hash_name = hashlib.sha256(
            (username.strip().lower()).encode()
        ).hexdigest()
        self.USER_PATH = f"data/Users/{self.hash_name}.sqlite"
    

    def _get_conn(self):
        conn = sqlite3.connect(self.USER_PATH)
        conn.execute(f"ATTACH DATABASE '{DB_PATH}' AS food_db")
        return conn
    

    def add_profile_details(self, Name, age, gender, weight, height, activity):

        conn = sqlite3.connect(self.USER_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO user_profile
            (Name, age, gender, weight, height, activity_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (Name, age, gender, weight, height, activity))

        conn.commit()
        conn.close()

    def get_profile_details(self, username):
        conn = sqlite3.connect(self.USER_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT age, gender, weight, height, activity_level
            FROM user_profile
        """)

        result = cursor.fetchone()
        conn.close()
        return result
 
    # -------------------------
    # FOOD LOOKUP
    # -------------------------

    def get_name(self):
        conn = sqlite3.connect(self.USER_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT Name FROM user_profile")
        name = cursor.fetchone()
        conn.close()
        return name
    
    def get_food_info(self, food):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT calories_kcal, carbohydrates_g, protein_g,
                   fats_g, free_sugar_g, fibre_g
            FROM foods_master
            WHERE dish_name = ?
        """, (food,))

        result = cursor.fetchone()
        conn.close()
        return result

    # -------------------------
    # FUZZY SEARCH
    # -------------------------
    def get_all_food_names(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT dish_name FROM foods_master")
        foods = [row[0] for row in cursor.fetchall()]

        conn.close()
        return foods

    def suggest_similar_foods(self, query, limit=5):
        foods = self.get_all_food_names()

        matches = process.extract(
            query,
            foods,
            scorer=fuzz.partial_ratio,
            limit=limit
        )

        return [name for name, score, _ in matches]

    # -------------------------
    # CALCULATION (PER 100g → quantity)
    # -------------------------
    def calculate_nutrition(self, nutrition, quantity):
        return tuple(x * quantity / 100 for x in nutrition)

    # -------------------------
    # ADD FOOD TO MEAL
    # -------------------------
    def add_food_to_meal(self, meal_type: str, food, quantity=100, date=DATE):

        nutrition = self.get_food_info(food)

        meal_type = meal_type.upper()
        meal_type = getattr(MealType, meal_type)

        if nutrition is None:
            print("Food not found")
            return

        conn = sqlite3.connect(self.USER_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO meals
            (meal_type, dish_name, quantity_g, meal_time)
            VALUES (?, ?, ?, ?)
        """, (
            meal_type,
            food,
            quantity,
            date
        ))

        conn.commit()
        conn.close()

    # -------------------------
    # CALCULATE SINGLE MEAL TOTAL
    # -------------------------
    def calculate_meal_cals(self, meal_type, date=DATE):

        meal_type = meal_type.upper()
        meal_type = getattr(MealType, meal_type)

        conn = self._get_conn()
        cursor = conn.cursor()

        # ✅ FIXED: removed self-join explosion
        cursor.execute("""
            SELECT
                SUM((mi.quantity_g / 100.0) * f.calories_kcal),
                SUM((mi.quantity_g / 100.0) * f.carbohydrates_g),
                SUM((mi.quantity_g / 100.0) * f.protein_g),
                SUM((mi.quantity_g / 100.0) * f.fats_g),
                SUM((mi.quantity_g / 100.0) * f.fibre_g),
                SUM((mi.quantity_g / 100.0) * f.free_sugar_g)
            FROM meals mi
            JOIN food_db.foods_master f
                ON mi.dish_name = f.dish_name
            WHERE mi.meal_type = ?
            AND DATE(mi.meal_time) = ?
        """, (meal_type, date))

        result = cursor.fetchone()
        conn.close()

        if result is None:
            return (0, 0, 0, 0, 0, 0)

        return tuple(x or 0 for x in result)

    # -------------------------
    # DAILY TOTAL
    # -------------------------
    def calculate_daily_macros(self, date=DATE):

        conn = self._get_conn()
        cursor = conn.cursor()

        # ✅ FIXED: removed self-join explosion
        cursor.execute("""
            SELECT
                SUM((mi.quantity_g / 100.0) * f.calories_kcal),
                SUM((mi.quantity_g / 100.0) * f.carbohydrates_g),
                SUM((mi.quantity_g / 100.0) * f.protein_g),
                SUM((mi.quantity_g / 100.0) * f.fats_g),
                SUM((mi.quantity_g / 100.0) * f.fibre_g),
                SUM((mi.quantity_g / 100.0) * f.free_sugar_g)
            FROM meals mi
            JOIN food_db.foods_master f
                ON mi.dish_name = f.dish_name
            WHERE DATE(mi.meal_time) = ?
        """, (date,))

        result = cursor.fetchone()
        conn.close()

        if result is None:
            return (0, 0, 0, 0, 0, 0)

        return tuple(x or 0 for x in result)

    # -------------------------
    # EDIT / DELETE ENTRY
    # -------------------------
    def change_entry(self, item_id, new_quantity=None, delete_entry=False):

        conn = self._get_conn()
        cursor = conn.cursor()

        if delete_entry:
            cursor.execute(
                "DELETE FROM meals WHERE item_id=?",
                (item_id,)
            )
            conn.commit()
            conn.close()
            return "Entry deleted"

        if new_quantity is None:
            conn.close()
            return "No quantity provided"

        cursor.execute("""
            UPDATE meals
            SET quantity_g=?
            WHERE item_id=?
        """, (new_quantity, item_id))

        conn.commit()
        conn.close()

        return "Entry updated"
    
    def get_meal_entries(self, meal_type, date=DATE):

        meal_type = meal_type.upper()
        meal_type = getattr(MealType, meal_type)

        conn = self._get_conn()

        # ✅ FIXED: removed self-join explosion
        query = """
            SELECT
                mi.item_id,
                mi.dish_name,
                mi.quantity_g,
                (mi.quantity_g / 100.0) * f.calories_kcal AS calories,
                (mi.quantity_g / 100.0) * f.carbohydrates_g AS carbs,
                (mi.quantity_g / 100.0) * f.protein_g AS protein,
                (mi.quantity_g / 100.0) * f.fats_g AS fats,
                (mi.quantity_g / 100.0) * f.fibre_g AS fibre,
                (mi.quantity_g / 100.0) * f.free_sugar_g AS sugar
            FROM meals mi
            JOIN food_db.foods_master f
                ON mi.dish_name = f.dish_name
            WHERE mi.meal_type = ?
            AND DATE(mi.meal_time) = ?
        """

        df = pd.read_sql_query(query, conn, params=(meal_type, date))
        conn.close()
        return df

    # -------------------------
    # YOLO DETECTION
    # -------------------------
    def detect_food(self, img):
        if img is None:
            return None

        image = Image.open(img).convert("RGB")

        results = MODEL.predict(
            image,
            imgsz=640,
            conf=0.5,
            save=False
        )

        result = results[0]
        detected_names = [MODEL.names[int(c)] for c in result.boxes.cls]

        class_counts = Counter(detected_names)

        return class_counts, detected_names